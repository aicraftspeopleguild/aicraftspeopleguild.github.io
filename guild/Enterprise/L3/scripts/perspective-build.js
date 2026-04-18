#!/usr/bin/env node
// @tag-event
// {
//   "id": "perspective-build:on-components-changed",
//   "listens": {
//     "kind": "on_transition",
//     "tag": "components.registry.changed",
//     "from": "*",
//     "to": "CHANGED"
//   },
//   "writes": [
//     "perspective.rebuilt_at"
//   ]
// }
// @end-tag-event
/**
 * Perspective-compatible view renderer.
 *
 * Reads:
 *   - guild/Enterprise/L2/hmi/web/perspective/components/registry.json  (acg.* type defs)
 *   - guild/Enterprise/L2/hmi/web/perspective/views/<slug>.view.json    (Perspective view)
 *   - guild/Enterprise/L2/hmi/web/perspective/data/<slug>.data.json     (optional data)
 *
 * Writes:
 *   - guild/web/dist/p-<slug>.html
 *
 * View schema (top-level: {custom, params, propConfig, props, root}) and
 * per-node schema (type, meta, position, props, propConfig, children) match
 * Ignition Perspective. Bindings supported: property, expression, data.
 */
const fs = require('fs');
const path = require('path');

const SCRIPTS_DIR = path.resolve(__dirname);
const WEB_ROOT = path.resolve(SCRIPTS_DIR, '..');
const REPO_ROOT = path.resolve(WEB_ROOT, '..', '..');
const PSP_DIR = path.join(WEB_ROOT, 'perspective');
const DIST_DIR = path.join(WEB_ROOT, 'dist');

const loadJSON = p => JSON.parse(fs.readFileSync(p, 'utf8'));
const escapeHtml = s => String(s == null ? '' : s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;').replace(/'/g, '&#39;');

// Resolve a dotted path against the view context.
function getPath(ctx, p) {
  if (!p) return undefined;
  const parts = p.split('.');
  let cur = ctx;
  for (const k of parts) {
    if (cur == null) return undefined;
    if (/^\d+$/.test(k) && Array.isArray(cur)) cur = cur[Number(k)];
    else cur = cur[k];
  }
  return cur;
}

// Resolve a binding spec to a value.
function resolveBinding(binding, ctx) {
  if (!binding || !binding.type) return undefined;
  const cfg = binding.config || {};
  if (binding.type === 'property') return getPath(ctx, cfg.path);
  if (binding.type === 'data') {
    const src = ctx[cfg.source] || (ctx.data && ctx.data[cfg.source]);
    if (src == null) return undefined;
    if (!cfg.path || cfg.path === '$') return src;
    return getPath({ $: src }, cfg.path);
  }
  if (binding.type === 'expression') {
    // Minimal substitution: {path} -> ctx value (strings concatenable)
    return (cfg.expression || '').replace(/\{([^}]+)\}/g, (_, p) => {
      const v = getPath(ctx, p);
      return v == null ? '' : String(v);
    }).replace(/^"|"$/g, '');
  }
  return undefined;
}

// Resolve effective props for a node: defaults + propConfig bindings.
function resolveProps(node, ctx) {
  const out = Object.assign({}, node.props || {});
  const pc = node.propConfig || {};
  for (const key of Object.keys(pc)) {
    if (!key.startsWith('props.')) continue;
    const field = key.substring('props.'.length);
    const val = resolveBinding(pc[key].binding, ctx);
    if (val !== undefined) out[field] = val;
  }
  return out;
}

// Mustache-lite interpolation with nested-section looping, triple-brace
// unescaped, and slot:NAME substitution.
function interpolate(tpl, props, slotsHTML) {
  if (!tpl) return '';
  let out = tpl;
  for (let g = 0; g < 10; g++) {
    const before = out;
    out = out.replace(
      /\{\{\s*#(\w+)\s*\}\}((?:(?!\{\{\s*#\w+\s*\}\})[\s\S])*?)\{\{\s*\/\1\s*\}\}/g,
      (_, k, inner) => {
        const v = props[k];
        if (v == null || v === false || v === '' || (Array.isArray(v) && v.length === 0)) return '';
        if (Array.isArray(v)) return v.map(i => inner.replace(/\{\{\s*\.\s*\}\}/g, escapeHtml(String(i)))).join('');
        return inner;
      }
    );
    if (out === before) break;
  }
  out = out.replace(/\{\{\{\s*(\w+)\s*\}\}\}/g, (_, k) => {
    const v = props[k];
    return v == null ? '' : String(v);
  });
  out = out.replace(/\{\{\s*slot:(\w+)\s*\}\}/g, (_, n) => slotsHTML[n] || '');
  out = out.replace(/\{\{\s*(\w+)\s*\}\}/g, (_, k) => {
    const v = props[k];
    return v == null ? '' : escapeHtml(String(v));
  });
  return out;
}

function renderNode(node, ctx, registry) {
  if (!node || !node.type) return '';
  const def = registry.types[node.type];
  if (!def) {
    console.warn(`[perspective] unknown type: ${node.type}`);
    return `<!-- unknown:${node.type} -->`;
  }
  const props = resolveProps(node, ctx);

  // Render children grouped by slot (via meta.slot, default slot otherwise)
  const slots = { default: '' };
  if (Array.isArray(node.children)) {
    for (const c of node.children) {
      const slotName = (c.meta && c.meta.slot) || 'default';
      slots[slotName] = (slots[slotName] || '') + renderNode(c, ctx, registry);
    }
  }

  // Build class list
  let cls = def.cssClass || '';
  if (def.propsToClass) {
    for (const p of def.propsToClass) {
      if (props[p]) cls += ' ' + props[p];
    }
  }
  cls = cls.trim();

  // Tag may be a template (e.g., "h{{ level }}" for headings)
  let tag = def.tag || 'div';
  if (tag.includes('{{')) tag = interpolate(tag, props, slots).trim() || 'div';

  // Resolve attributes
  let attrs = cls ? ` class="${escapeHtml(cls)}"` : '';
  if (def.propsToAttr) {
    for (const [p, a] of Object.entries(def.propsToAttr)) {
      if (props[p] != null && props[p] !== '') attrs += ` ${a}="${escapeHtml(String(props[p]))}"`;
    }
  }

  // Compute inner
  const tpl = def.template || '';
  let inner = interpolate(tpl, props, slots);

  if (tag === 'fragment') return inner;
  if (def.selfClosing) return `<${tag}${attrs}>`;
  return `<${tag}${attrs}>${inner}</${tag}>`;
}

function wrapDocument(title, bodyHTML, custom) {
  custom = custom || {};
  // Default CSS: main.css from dist/ perspective (../style/main.css).
  // Any view may override via view.custom.stylesheets (array of repo-relative paths).
  const sheets = custom.stylesheets || ['../style/main.css'];
  const sheetLinks = sheets.map(s => `<link rel="stylesheet" href="${escapeHtml(s)}">`).join('\n    ');
  const headExtra = custom.headExtra || '';
  const bodyExtra = custom.bodyExtra || '';
  const bodyAttrs = custom.bodyClass ? ` class="${escapeHtml(custom.bodyClass)}"` : '';
  const analyticsId = custom.analyticsId || 'G-Z1CEF69ZSH';
  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${escapeHtml(title)}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Work+Sans:wght@300;400;600&family=Courier+Prime:wght@400;700&display=swap" rel="stylesheet">
    <script async src="https://www.googletagmanager.com/gtag/js?id=${escapeHtml(analyticsId)}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', '${escapeHtml(analyticsId)}');
    </script>
    ${sheetLinks}
    ${headExtra}
</head>
<body${bodyAttrs}>
${bodyHTML}
${bodyExtra}
</body>
</html>
`;
}

function renderView(viewFile, dataFile) {
  const view = loadJSON(viewFile);
  const registry = loadJSON(path.join(PSP_DIR, 'components', 'registry.json'));

  const ctx = {
    view: {
      params: view.params || {},
      custom: view.custom || {},
      props:  view.props  || {}
    }
  };
  if (dataFile && fs.existsSync(dataFile)) {
    const data = loadJSON(dataFile);
    Object.assign(ctx, data);
  }

  const body = renderNode(view.root, ctx, registry);
  const title = ctx.view.params.title || ctx.view.params.defaultTitle || 'ACG';
  return wrapDocument(title, body, view.custom || {});
}

// Determine output path for a view. If view.custom.output is set, it's
// treated as repo-rooted; otherwise default to guild/web/dist/p-<slug>.html
function outputPath(view, slug) {
  const out = view && view.custom && view.custom.output;
  if (out) return path.join(REPO_ROOT, out);
  return path.join(DIST_DIR, `p-${slug}.html`);
}

// Recursively collect *.view.json from a directory.
function collectViews(root) {
  if (!fs.existsSync(root)) return [];
  const out = [];
  for (const entry of fs.readdirSync(root, { withFileTypes: true })) {
    const full = path.join(root, entry.name);
    if (entry.isDirectory())      out.push(...collectViews(full));
    else if (entry.name.endsWith('.view.json')) out.push(full);
  }
  return out;
}

function main() {
  if (!fs.existsSync(DIST_DIR)) fs.mkdirSync(DIST_DIR, { recursive: true });

  // Scan both canonical authoring location and the root index/ directory.
  const viewFiles = [
    ...collectViews(path.join(PSP_DIR, 'views')),
    ...collectViews(path.join(REPO_ROOT, 'index')),
  ];

  let count = 0, skipped = 0;
  for (const viewFile of viewFiles) {
    const slug = path.basename(viewFile).replace(/\.view\.json$/, '').replace(/^index$/, 'index');
    const view = loadJSON(viewFile);
    // Partial views (docks, body fragments) are composed into other views;
    // they don't need standalone dist/ output.
    if (view.custom && view.custom.partial) {
      skipped++;
      continue;
    }
    // Data file: look next to the view first, else in perspective/data/
    const localData = path.join(path.dirname(viewFile), `${slug}.data.json`);
    const dataFile  = fs.existsSync(localData)
      ? localData
      : path.join(PSP_DIR, 'data', `${slug}.data.json`);
    const html = renderView(viewFile, dataFile);
    const out = outputPath(view, slug);
    fs.mkdirSync(path.dirname(out), { recursive: true });
    fs.writeFileSync(out, html, 'utf8');
    const rel = path.relative(REPO_ROOT, out).split(path.sep).join('/');
    console.log(`[perspective] ${slug} → ${rel} (${html.length} bytes)`);
    count++;
  }
  if (skipped) console.log(`[perspective] skipped ${skipped} partial views`);
  console.log(`[perspective] rendered ${count} views`);
}

if (require.main === module) {
  try { main(); } catch (e) { console.error(e); process.exit(1); }
}
module.exports = { renderView, renderNode, resolveBinding, interpolate };
