#!/usr/bin/env node
/**
 * ACG Static Site Builder
 *
 * Reads Path UDT instances → Page JSONs → View JSONs → Component registry.
 * Walks each view's component tree, binds data, and emits fully-rendered HTML.
 *
 * Output: guild/web/static/<slug>.html for every published Path.
 *
 * Usage:   node guild/web/build.js
 * From:    repo root
 */
const fs = require('fs');
const path = require('path');

// __dirname is guild/web/scripts — web root is one level up
const WEB_ROOT = path.resolve(__dirname, '..');
const REPO_ROOT = path.resolve(WEB_ROOT, '..', '..');

/**
 * Resolve a path stored in a UDT instance.
 * - "guild/..." → repo-rooted (lets app pages live outside guild/web/)
 * - everything else → relative to guild/web/ (legacy convention)
 */
function resolvePath(p) {
  if (!p) return p;
  if (p.startsWith('guild/') || path.isAbsolute(p)) return path.join(REPO_ROOT, p);
  return path.join(WEB_ROOT, p);
}

// ── Load JSON with error context ────────────────────────────────────
function loadJSON(p) {
  try {
    return JSON.parse(fs.readFileSync(p, 'utf8'));
  } catch (e) {
    console.error(`[build] Failed to load ${p}: ${e.message}`);
    throw e;
  }
}

// ── Binding Resolution ──────────────────────────────────────────────
function resolve(expr, ctx) {
  if (typeof expr !== 'string') return expr;
  const pure = /^\{\{\s*(.+?)\s*\}\}$/.exec(expr);
  if (pure) return getPath(ctx, pure[1].trim());
  return expr.replace(/\{\{\s*(.+?)\s*\}\}/g, (_, p) => {
    const v = getPath(ctx, p.trim());
    return v == null ? '' : String(v);
  });
}

function getPath(obj, p) {
  const parts = p.split('.');
  let cur = obj;
  for (const k of parts) {
    if (cur == null) return undefined;
    cur = cur[k];
  }
  return cur;
}

function isFalsy(v) {
  if (v == null || v === false || v === 0 || v === '') return true;
  if (Array.isArray(v) && v.length === 0) return true;
  return false;
}

// ── Template Interpolation (Mustache-lite) ──────────────────────────
function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function interpolate(tpl, props) {
  if (!tpl) return '';
  let out = tpl;
  // Section: {{ #key }}...{{ /key }} — loop to handle nested sections
  for (let guard = 0; guard < 10; guard++) {
    const before = out;
    out = out.replace(
      /\{\{\s*#(\w+)\s*\}\}((?:(?!\{\{\s*#\w+\s*\}\})[\s\S])*?)\{\{\s*\/\1\s*\}\}/g,
      (_, k, inner) => {
        const v = props[k];
        if (isFalsy(v)) return '';
        if (Array.isArray(v)) {
          return v.map(item =>
            inner.replace(/\{\{\s*\.\s*\}\}/g, escapeHtml(String(item)))
          ).join('');
        }
        return inner;
      }
    );
    if (out === before) break;
  }
  // Inverted: {{ ^key }}...{{ /key }}
  out = out.replace(
    /\{\{\s*\^(\w+)\s*\}\}([\s\S]*?)\{\{\s*\/\1\s*\}\}/g,
    (_, k, inner) => isFalsy(props[k]) ? inner : ''
  );
  // Unescaped: {{{ key }}} — emits raw string (for pre-rendered HTML content)
  out = out.replace(/\{\{\{\s*(\w+)\s*\}\}\}/g, (_, k) => {
    const v = props[k];
    return v == null ? '' : String(v);
  });
  // Simple escaped: {{ key }}
  out = out.replace(/\{\{\s*(\w+)\s*\}\}/g, (_, k) => {
    const v = props[k];
    return v == null ? '' : escapeHtml(String(v));
  });
  return out;
}

// ── Component Tree → HTML ───────────────────────────────────────────
function renderNode(node, ctx, components) {
  if (!node || !node.type) return '';

  if (node.when !== undefined && isFalsy(resolve(node.when, ctx))) return '';

  const boundProps = {};
  for (const k of Object.keys(node.props || {})) {
    boundProps[k] = resolve(node.props[k], ctx);
  }

  const comp = components[node.type];
  if (!comp) {
    console.warn(`[build] Unknown component: ${node.type}`);
    return `<!-- unknown:${node.type} -->`;
  }

  const tag = comp.parameters.tag || 'div';
  const cssClass = [comp.parameters.cssClass || '', boundProps.cssVariant || '', boundProps.bodyClass || '']
    .filter(Boolean).join(' ').trim();

  // Render children first (so they can fill slots)
  let childrenHTML = '';
  if (Array.isArray(node.children)) {
    for (const c of node.children) childrenHTML += renderNode(c, ctx, components);
  }
  if (node.repeat) {
    const items = resolve('{{ ' + node.repeat.source + ' }}', ctx);
    if (Array.isArray(items)) {
      for (const item of items) {
        const childCtx = { ...ctx, [node.repeat.as]: item };
        childrenHTML += renderNode(node.repeat.template, childCtx, components);
      }
    }
  }

  let inner;
  if (comp.parameters.template) {
    inner = interpolate(comp.parameters.template, boundProps);
    // Replace slot tokens with rendered children
    inner = inner.replace(/\{\{\s*slot:default\s*\}\}/g, childrenHTML);
  } else {
    inner = childrenHTML;
  }

  // "fragment" tag means: emit inner only, no wrapping element
  if (tag === 'fragment') return inner;

  const classAttr = cssClass ? ` class="${escapeHtml(cssClass)}"` : '';
  return `<${tag}${classAttr}>${inner}</${tag}>`;
}

// ── Full Page HTML Wrapper ──────────────────────────────────────────

/** Convert a stylesheet path stored in page.json into a path that resolves
 *  from inside guild/web/dist/. Both web-relative ("style/main.css") and
 *  repo-rooted ("guild/web/style/main.css") inputs become "../style/main.css". */
function relativizeAssetForDist(p) {
  if (!p) return p;
  if (/^https?:\/\//.test(p)) return p;
  // Strip leading guild/web/ if present
  let rel = p.replace(/^guild\/web\//, '');
  // dist/ is a sibling of style/, assets/, etc., so go up one
  return '../' + rel.replace(/^\.\//, '').replace(/^\/+/, '');
}

function wrapDocument(title, stylesheets, bodyHTML, extraHead = '') {
  const styles = (stylesheets || []).map(
    s => `<link rel="stylesheet" href="${escapeHtml(relativizeAssetForDist(s))}">`
  ).join('\n    ');
  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${escapeHtml(title)} — AI Craftspeople Guild</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Work+Sans:wght@300;400;600&family=Courier+Prime:wght@400;700&display=swap" rel="stylesheet">
    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-Z1CEF69ZSH"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-Z1CEF69ZSH');
    </script>
    ${styles}
    ${extraHead}
</head>
<body>
${bodyHTML}
</body>
</html>
`;
}

// ── Main Build Loop ─────────────────────────────────────────────────
function build() {
  console.log('[build] ACG static site builder starting');

  // Load component registry
  const registry = loadJSON(path.join(WEB_ROOT, 'components', 'registry.json'));
  const components = {};
  for (const name of Object.keys(registry.components)) {
    const src = path.join(WEB_ROOT, registry.components[name].src);
    if (fs.existsSync(src)) {
      components[name] = loadJSON(src);
    } else {
      console.warn(`[build] Missing component file: ${src}`);
    }
  }
  console.log(`[build] Loaded ${Object.keys(components).length} components`);

  // Load all Paths
  const pathsDir = path.join(WEB_ROOT, 'components', 'udts', 'instances', 'paths');
  const pathFiles = fs.readdirSync(pathsDir).filter(f => f.endsWith('.json'));
  const paths = pathFiles.map(f => loadJSON(path.join(pathsDir, f)));
  console.log(`[build] Loaded ${paths.length} paths`);

  let rendered = 0;
  let skipped = 0;

  for (const p of paths) {
    const pp = p.parameters;
    // Skip dynamic paths — they need a data source to enumerate instances
    if (pp.dynamic) {
      skipped++;
      continue;
    }
    if (pp.status !== 'published') {
      skipped++;
      continue;
    }

    // Load the Page (repo-rooted if path starts with "guild/", else web-rooted)
    const pageFile = resolvePath(pp.page);
    if (!fs.existsSync(pageFile)) {
      console.warn(`[build] Missing page: ${pageFile}`);
      skipped++;
      continue;
    }
    const page = loadJSON(pageFile);
    const pgParams = page.parameters;

    // Load the View
    const viewFile = resolvePath(pgParams.view);
    if (!fs.existsSync(viewFile)) {
      console.warn(`[build] Missing view: ${viewFile}`);
      skipped++;
      continue;
    }
    const view = loadJSON(viewFile);

    // Build data context
    const ctx = { page: pgParams, path: pp };
    if (pgParams.data) {
      for (const key of Object.keys(pgParams.data)) {
        const dataPath = resolvePath(pgParams.data[key]);
        if (fs.existsSync(dataPath)) {
          ctx[key] = loadJSON(dataPath);
        }
      }
    }

    // Render
    let bodyHTML;
    if (view.parameters.name === 'static-page') {
      // Static-page view just emits a link to the pre-rendered snapshot
      const src = pgParams.staticSrc || `static/${p.tags.id}.html`;
      bodyHTML = `<meta http-equiv="refresh" content="0; url=${escapeHtml(src)}">\n<p>Redirecting to <a href="${escapeHtml(src)}">${escapeHtml(pgParams.title)}</a>...</p>`;
    } else {
      bodyHTML = renderNode(view.parameters.root, ctx, components);
    }

    // Wrap in full HTML document
    const html = wrapDocument(pgParams.title, pgParams.stylesheets, bodyHTML);

    // Write output
    const outDir = path.join(WEB_ROOT, 'dist');
    if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
    const outFile = path.join(outDir, `${p.tags.id}.html`);
    fs.writeFileSync(outFile, html, 'utf8');
    console.log(`[build] ✓ ${p.tags.id} → dist/${p.tags.id}.html`);
    rendered++;
  }

  console.log(`\n[build] Done. Rendered: ${rendered}, Skipped: ${skipped}`);
}

if (require.main === module) {
  try { build(); } catch (e) { console.error(e); process.exit(1); }
}

module.exports = { build, renderNode, interpolate, resolve };
