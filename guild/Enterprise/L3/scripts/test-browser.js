#!/usr/bin/env node
// @tag-event
// {
//   "id": "test-browser:on-release-request",
//   "listens": {
//     "kind": "on_transition",
//     "tag": "release.request",
//     "from": "*",
//     "to": "RAISED"
//   },
//   "writes": [
//     "qa.browser.ok"
//   ]
// }
// @end-tag-event
/**
 * Headless-browser test harness using Playwright.
 *
 * Spins up a local HTTP server, opens the root index.html in a real browser,
 * clicks every #/slug nav link, takes a screenshot of each rendered view,
 * and collects:
 *   - network 4xx/5xx errors
 *   - console errors
 *   - whether #app has meaningful content after navigation
 *   - final rendered body length
 *
 * Output:
 *   guild/web/dist/screenshots/<slug>.png
 *   guild/web/dist/screenshots/test-report.json
 */
const { chromium } = require('playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const REPO = path.resolve(__dirname, '..', '..', '..');
const PORT = 8766;
const BASE = `http://127.0.0.1:${PORT}`;
const SHOTS = path.join(REPO, 'guild', 'web', 'dist', 'screenshots');

function startServer() {
  return new Promise((resolve, reject) => {
    const proc = spawn('python', ['-m', 'http.server', String(PORT), '--bind', '127.0.0.1'], {
      cwd: REPO, stdio: ['ignore', 'pipe', 'pipe']
    });
    let resolved = false;
    // Wait for the "Serving" line
    proc.stderr.on('data', d => {
      if (!resolved && /Serving HTTP/.test(d.toString())) {
        resolved = true; resolve(proc);
      }
    });
    // Fallback: assume up after 800ms
    setTimeout(() => { if (!resolved) { resolved = true; resolve(proc); } }, 800);
    proc.on('error', e => { if (!resolved) { resolved = true; reject(e); } });
  });
}

function hashRoutes(html) {
  const out = [];
  const re = /href="(#\/[^"]+)"/g;
  const seen = new Set();
  let m;
  while ((m = re.exec(html))) {
    if (seen.has(m[1])) continue;
    seen.add(m[1]); out.push(m[1]);
  }
  return out;
}

async function testRoute(page, route) {
  const errors = [];
  const onPageErr = e => errors.push(`page: ${e.message}`);
  const onConsole = msg => {
    if (msg.type() === 'error') errors.push(`console: ${msg.text()}`);
  };
  const onResponse = res => {
    if (res.status() >= 400) errors.push(`http ${res.status()}: ${res.url()}`);
  };
  page.on('pageerror', onPageErr);
  page.on('console', onConsole);
  page.on('response', onResponse);

  try {
    // Clear the hash first; then set to trigger hashchange
    await page.evaluate(() => { history.replaceState(null, '', '/'); });
    await page.goto(`${BASE}/${route}`, { waitUntil: 'networkidle', timeout: 8000 });

    // Wait up to 4s for either static content hidden + #app populated, OR for
    // the has-route class to be applied
    await page.waitForFunction(() => {
      var app = document.querySelector('#app');
      return document.body.classList.contains('has-route')
          && app && app.innerHTML.length > 500;
    }, { timeout: 10000 }).catch(() => {});

    const appContentLen = await page.evaluate(() => {
      const a = document.querySelector('#app');
      return a ? a.innerHTML.length : 0;
    });
    const appVisible = await page.evaluate(() => {
      const a = document.querySelector('#app');
      if (!a) return false;
      const r = a.getBoundingClientRect();
      return r.width > 0 && r.height > 0;
    });
    const hasRoute = await page.evaluate(() => document.body.classList.contains('has-route'));
    const title    = await page.title();

    // Screenshot
    const slug = route.replace(/^#\//, '').replace(/\//g, '_') || 'home';
    const shotPath = path.join(SHOTS, `${slug}.png`);
    await page.screenshot({ path: shotPath, fullPage: true });

    return {
      route, title, appContentLen, appVisible, hasRoute,
      screenshot: path.relative(REPO, shotPath).split(path.sep).join('/'),
      errors: errors.filter(e => !e.includes('favicon.ico'))  // harmless
    };
  } finally {
    page.off('pageerror', onPageErr);
    page.off('console', onConsole);
    page.off('response', onResponse);
  }
}

async function testHome(page) {
  const errors = [];
  page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
  page.on('pageerror', e => errors.push(`page: ${e.message}`));
  await page.goto(`${BASE}/`, { waitUntil: 'networkidle', timeout: 8000 });
  const shot = path.join(SHOTS, 'home.png');
  await page.screenshot({ path: shot, fullPage: true });
  const title = await page.title();
  const navCount = await page.locator('.top-nav a').count();
  const cardCount = await page.locator('.manifesto-card').count();
  return {
    route: '/', title, navCount, cardCount,
    screenshot: path.relative(REPO, shot).split(path.sep).join('/'),
    errors: errors.filter(e => !e.includes('favicon'))
  };
}

async function main() {
  fs.mkdirSync(SHOTS, { recursive: true });

  console.log(`Starting local server at ${BASE}...`);
  const server = await startServer();

  let browser;
  try {
    browser = await chromium.launch({ headless: true });
    const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
    const page = await ctx.newPage();

    console.log('\n[home] Loading /');
    const homeResult = await testHome(page);
    console.log(`  title: "${homeResult.title}"`);
    console.log(`  nav links: ${homeResult.navCount}, manifesto cards: ${homeResult.cardCount}`);
    console.log(`  screenshot: ${homeResult.screenshot}`);
    if (homeResult.errors.length) {
      console.log(`  errors:`);
      for (const e of homeResult.errors) console.log(`    - ${e}`);
    }

    // Read the freshly-rendered index.html via page and extract hash routes
    const html = await page.content();
    const routes = hashRoutes(html);
    console.log(`\nTesting ${routes.length} hash routes...`);

    const results = [homeResult];
    for (const r of routes) {
      const res = await testRoute(page, r);
      const ok = res.hasRoute && res.appContentLen > 200 && res.appVisible && res.errors.length === 0;
      const mark = ok ? '[OK]  ' : '[FAIL]';
      const vis = res.appVisible ? 'vis' : 'HIDDEN';
      console.log(`  ${mark} ${r.padEnd(22)} app=${res.appContentLen}b  ${vis}  errors=${res.errors.length}`);
      if (res.errors.length) {
        for (const e of res.errors.slice(0, 3)) console.log(`        ${e}`);
      }
      results.push(res);
    }

    // Report
    const report = {
      generated_at: new Date().toISOString(),
      base: BASE,
      total: results.length,
      passed: results.filter(r => r.route === '/' ? r.errors.length === 0
                                                  : r.hasRoute && r.appContentLen > 200 && r.appVisible && r.errors.length === 0).length,
      results
    };
    fs.writeFileSync(path.join(SHOTS, 'test-report.json'), JSON.stringify(report, null, 2));
    console.log(`\nReport: ${path.relative(REPO, path.join(SHOTS, 'test-report.json'))}`);
    console.log(`Screenshots: ${path.relative(REPO, SHOTS)}/`);
    console.log(`\n${report.passed}/${report.total} passed`);

    process.exit(report.passed === report.total ? 0 : 1);
  } finally {
    if (browser) await browser.close();
    try { server.kill(); } catch {}
  }
}

main().catch(e => { console.error(e); process.exit(1); });
