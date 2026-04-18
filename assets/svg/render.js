/**
 * assets/svg/render.js
 * Universal SVG template renderer — {{TOKEN}} → value replacement
 *
 * All token values are XML-escaped before injection (prevents SVG injection).
 *
 * ── Browser (ES module) ─────────────────────────────────────────────────────
 *   import { renderSVG, injectSVG, svgBlobURL } from './assets/svg/render.js';
 *
 *   // Inline rendered SVG into a DOM element
 *   await injectSVG(document.querySelector('#banner'), './assets/svg/organisms/guild-banner.svg', {
 *     TAGLINE:  'ISA-95 live control-plane',
 *     PAPERS:   '25',
 *     MEMBERS:  '8',
 *     COMMITS:  '142',
 *     STATUS:   'LIVE',
 *     TS:       new Date().toISOString(),
 *     VERSION:  'v1.0.0',
 *     LOCATION: 'github.com/aicraftspeopleguild',
 *   });
 *
 *   // Or get a blob: URL to set on <img src>
 *   img.src = await svgBlobURL('./assets/svg/atoms/tag-chip.svg', {
 *     LABEL: 'isa-95', BG_COLOR: '#161b22', BORDER_COLOR: '#30363d', TEXT_COLOR: '#8b949e',
 *   });
 *
 * ── Node.js CLI (GitHub Actions / build script) ─────────────────────────────
 *   node assets/svg/render.js <template.svg> <params.json | '{"K":"v"}'> [output.svg]
 *
 *   # Inline JSON:
 *   node assets/svg/render.js assets/svg/organisms/guild-banner.svg \
 *     '{"TAGLINE":"ISA-95 live control-plane","PAPERS":"25","MEMBERS":"8",...}' \
 *     guild/Enterprise/L4/svg/guild-banner.svg
 *
 *   # Params file:
 *   node assets/svg/render.js template.svg params.json output.svg
 *
 * ── Token convention ─────────────────────────────────────────────────────────
 *   Tokens are UPPER_SNAKE_CASE surrounded by double curly braces: {{TOKEN_NAME}}
 *   Each SVG template lists its tokens in a comment near the top.
 *   Missing tokens are left as-is (the placeholder remains visible — useful for debugging).
 *
 * ── level-dots helper ─────────────────────────────────────────────────────────
 *   import { levelDotParams } from './assets/svg/render.js';
 *   const dotParams = levelDotParams(3, 5, '#3fb950');  // level 3 of 5
 *   // → { D1_FILL:'#3fb950', D2_FILL:'#3fb950', D3_FILL:'#3fb950', D4_FILL:'#21262d', D5_FILL:'#21262d',
 *   //     LEVEL_TEXT:'3/5' }
 */

// ── Core ─────────────────────────────────────────────────────────────────────

const XML_MAP = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' };

/** XML-escape a string so it is safe to inject into SVG attribute values and text nodes. */
export function escXML(str) {
  return String(str).replace(/[&<>"']/g, c => XML_MAP[c]);
}

/**
 * Replace every {{TOKEN}} in `template` with its value from `params`.
 * Values are XML-escaped automatically.
 * @param {string} template  — raw SVG template text
 * @param {Record<string,string|number>} params — token → value map
 * @returns {string} rendered SVG
 */
export function renderSVG(template, params) {
  return Object.entries(params).reduce(
    (svg, [key, val]) => svg.replaceAll(`{{${key}}}`, escXML(val)),
    template,
  );
}

// ── Browser helpers ───────────────────────────────────────────────────────────

/**
 * Fetch a template SVG, render with params, and set the innerHTML of `el`.
 * The SVG is inlined — CSS custom properties from the page flow in,
 * and SMIL animations run natively.
 * @param {Element} el
 * @param {string} url — absolute or relative URL of the .svg template
 * @param {Record<string,string|number>} params
 */
export async function injectSVG(el, url, params) {
  const text = await fetch(url).then(r => {
    if (!r.ok) throw new Error(`SVG fetch failed: ${r.status} ${url}`);
    return r.text();
  });
  el.innerHTML = renderSVG(text, params);
}

/**
 * Render a template to a `blob:` URL usable as `<img src>`.
 * Call URL.revokeObjectURL(url) when done to free memory.
 * @param {string} url — template URL
 * @param {Record<string,string|number>} params
 * @returns {Promise<string>} blob URL
 */
export async function svgBlobURL(url, params) {
  const text = await fetch(url).then(r => r.text());
  const svg  = renderSVG(text, params);
  return URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml' }));
}

// ── Param helpers ─────────────────────────────────────────────────────────────

/**
 * Build fill-color params for atoms/level-dots.svg.
 * @param {number} level   — current level (1-based)
 * @param {number} max     — total dots (default 5)
 * @param {string} onColor — fill color for active dots (default guild green)
 * @param {string} offColor — fill color for inactive dots
 * @returns {Record<string,string>}
 */
export function levelDotParams(level, max = 5, onColor = '#3fb950', offColor = '#21262d') {
  const params = { LEVEL_TEXT: `${level}/${max}` };
  for (let i = 1; i <= max; i++) {
    params[`D${i}_FILL`] = i <= level ? onColor : offColor;
  }
  return params;
}

/**
 * Map a severity string to alert-banner color tokens.
 * @param {'INFO'|'OK'|'WARN'|'ERROR'} severity
 * @returns {{ COLOR: string, BG_COLOR: string }}
 */
export function severityColors(severity) {
  const map = {
    INFO:  { COLOR: '#79c0ff', BG_COLOR: '#0d1f2e' },
    OK:    { COLOR: '#3fb950', BG_COLOR: '#1b3a27' },
    WARN:  { COLOR: '#e3b341', BG_COLOR: '#3a2e10' },
    ERROR: { COLOR: '#ff7b72', BG_COLOR: '#3a1010' },
  };
  return map[severity.toUpperCase()] ?? map.INFO;
}

// ── Node.js CLI ───────────────────────────────────────────────────────────────
// Usage: node assets/svg/render.js <template.svg> <params.json | '{...}'> [output.svg]

if (
  typeof process !== 'undefined' &&
  typeof process.argv !== 'undefined' &&
  process.argv[1]?.replace(/\\/g, '/').includes('svg/render')
) {
  const { readFileSync, writeFileSync } = await import('fs');
  const [,, templatePath, paramsArg, outPath] = process.argv;

  if (!templatePath || !paramsArg) {
    console.error(
      'Usage: node assets/svg/render.js <template.svg> <params.json | \'{...}\'> [output.svg]',
    );
    process.exit(1);
  }

  const template = readFileSync(templatePath, 'utf8');
  const params   = paramsArg.trimStart().startsWith('{')
    ? JSON.parse(paramsArg)
    : JSON.parse(readFileSync(paramsArg, 'utf8'));

  const result = renderSVG(template, params);

  if (outPath) {
    writeFileSync(outPath, result, 'utf8');
    console.error(`✓ wrote ${outPath}`);
  } else {
    process.stdout.write(result);
  }
}
