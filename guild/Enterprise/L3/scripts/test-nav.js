#!/usr/bin/env node
// @tag-event
// {
//   "id": "test-nav:on-release-request",
//   "listens": {
//     "kind": "on_transition",
//     "tag": "release.request",
//     "from": "*",
//     "to": "RAISED"
//   },
//   "writes": [
//     "qa.nav.ok"
//   ]
// }
// @end-tag-event
/**
 * Simulates browser navigation through the hash-route renderer for every
 * #/slug link in index.html. Uses the same tree-walk logic as build.js,
 * fetching via HTTP from a local server (default: http://127.0.0.1:8765).
 *
 * For each link:
 *   1. Parse hash route
 *   2. Match against site-map
 *   3. Fetch page.json
 *   4. Fetch view.json
 *   5. Fetch any data sources
 *   6. Fetch every component referenced
 *   7. Render the view tree
 *   8. Assert output contains expected markers
 */
const fs = require('fs');
const path = require('path');
const http = require('http');

const BASE = process.env.TEST_BASE || 'http://127.0.0.1:8765';

function fetchURL(url) {
  return new Promise((resolve, reject) => {
    http.get(url, res => {
      if (res.statusCode !== 200) {
        return reject(new Error(`${res.statusCode} ${url}`));
      }
      let data = '';
      res.setEncoding('utf8');
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    }).on('error', reject);
  });
}

async function fetchJSON(relPath) {
  return JSON.parse(await fetchURL(BASE + relPath));
}

// Import render helpers from build.js (they mirror renderer.js logic)
const builder = require('./build.js');

function extractHashRoutes(html) {
  const seen = new Set();
  const re = /href="(#\/[^"]+)"/g;
  let m;
  while ((m = re.exec(html))) seen.add(m[1]);
  return Array.from(seen);
}

function matchRoute(sitemap, pathname) {
  for (const route of sitemap.routes) {
    if (route.dynamic) {
      const pat = route.path.replace(/:(\w+)/g, '([^/]+)');
      const re = new RegExp('^' + pat + '$');
      const m = pathname.match(re);
      if (m) return { route, params: { slug: m[1] } };
    } else if (route.path === pathname) {
      return { route, params: {} };
    }
  }
  return null;
}

async function testRoute(hashRoute, sitemap, registry) {
  const pathname = hashRoute.slice(1); // "#/charter" -> "/charter"
  const match = matchRoute(sitemap, pathname);
  if (!match) return { route: hashRoute, ok: false, reason: 'no route match' };

  const basePath = sitemap.base || '/';
  let pageJSON, viewJSON, dataCtx = {};

  try {
    pageJSON = await fetchJSON(basePath + match.route.page);
  } catch (e) {
    return { route: hashRoute, ok: false, reason: `page.json: ${e.message}` };
  }

  try {
    viewJSON = await fetchJSON(basePath + pageJSON.parameters.view);
  } catch (e) {
    return { route: hashRoute, ok: false, reason: `view.json: ${e.message}` };
  }

  // Initialize context with page params, then overlay data sources
  // (data keyed by "page" wins — matches renderer.js behavior)
  dataCtx.page = pageJSON.parameters;
  dataCtx.path = match.route;
  if (pageJSON.parameters.data) {
    for (const [key, src] of Object.entries(pageJSON.parameters.data)) {
      let p = src;
      if (match.params.slug) p = p.replace(':slug', match.params.slug);
      try {
        dataCtx[key] = await fetchJSON(basePath + p);
      } catch (e) {
        return { route: hashRoute, ok: false, reason: `data.${key}: ${e.message}` };
      }
    }
  }

  // Fetch all components upfront (mirrors new renderer.js behavior)
  const components = {};
  for (const name of Object.keys(registry.components)) {
    try {
      components[name] = await fetchJSON(basePath + registry.components[name].src);
    } catch (e) {
      return { route: hashRoute, ok: false, reason: `component ${name}: ${e.message}` };
    }
  }

  // Render the view tree using build.js's renderNode (same logic as client)
  let html;
  try {
    html = builder.renderNode(viewJSON.parameters.root, dataCtx, components);
  } catch (e) {
    return { route: hashRoute, ok: false, reason: `render: ${e.message}` };
  }

  // Assertions
  if (!html || html.length < 200) {
    return { route: hashRoute, ok: false, reason: `tiny output (${html ? html.length : 0} chars)` };
  }
  // Any leftover mustache tokens?
  if (/\{\{[^}]*\}\}/.test(html)) {
    const stray = html.match(/\{\{[^}]*\}\}/g).slice(0, 3);
    return { route: hashRoute, ok: false, reason: `stray tokens: ${stray.join(', ')}` };
  }
  // Basic structure
  if (!/<header[\s>]/.test(html) || !/<main[\s>]/.test(html) || !/<footer[\s>]/.test(html)) {
    return { route: hashRoute, ok: false, reason: 'missing header/main/footer' };
  }

  return { route: hashRoute, ok: true, bytes: html.length, title: pageJSON.parameters.title };
}

async function main() {
  console.log(`Testing navigation against ${BASE}`);

  const indexHTML = await fetchURL(BASE + '/');
  const routes = extractHashRoutes(indexHTML);
  console.log(`Found ${routes.length} hash routes in index.html:\n`);

  const sitemap = await fetchJSON('/guild/Enterprise/L2/hmi/web/site-map.json');
  const registry = await fetchJSON('/guild/Enterprise/L2/hmi/web/components/registry.json');

  let passed = 0, failed = 0;
  const results = [];
  for (const r of routes) {
    const res = await testRoute(r, sitemap, registry);
    results.push(res);
    if (res.ok) {
      console.log(`  [OK]   ${r.padEnd(25)} ${res.title} (${res.bytes} bytes)`);
      passed++;
    } else {
      console.log(`  [FAIL] ${r.padEnd(25)} ${res.reason}`);
      failed++;
    }
  }

  console.log(`\nSummary: ${passed} passed, ${failed} failed`);
  process.exit(failed ? 1 : 0);
}

main().catch(e => { console.error(e); process.exit(1); });
