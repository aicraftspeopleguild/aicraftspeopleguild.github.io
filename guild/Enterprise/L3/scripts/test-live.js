#!/usr/bin/env node
// @tag-event
// {
//   "id": "test-live:on-release-request",
//   "listens": {
//     "kind": "on_transition",
//     "tag": "release.request",
//     "from": "*",
//     "to": "RAISED"
//   },
//   "writes": [
//     "qa.live.ok"
//   ]
// }
// @end-tag-event
/**
 * Live-site smoke test via Playwright.
 *
 * Loads the live teslasolar Pages URL (or any URL in TEST_BASE), clicks through
 * a handful of hash routes, captures screenshots + console errors + network
 * failures, and dumps a report.
 *
 * Output:
 *   guild/web/dist/live-shots/<slug>.png
 *   guild/web/dist/live-shots/report.json
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE = process.env.TEST_BASE || 'https://teslasolar.github.io/aicraftspeopleguild.github.io/';
const OUT  = path.resolve(__dirname, '..', 'dist', 'live-shots');

const ROUTES = [
  { slug: 'home',       hash: '' },
  { slug: 'charter',    hash: '#/charter' },
  { slug: 'conduct',    hash: '#/code-of-conduct' },
  { slug: 'papers',     hash: '#/white-papers' },
  { slug: 'members',    hash: '#/members' },
  { slug: 'submit',     hash: 'guild/Enterprise/L1/forms/submit/', literal: true },
];

function slugify(s) { return s.replace(/[^\w.-]+/g, '_'); }

async function main() {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const ctx     = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page    = await ctx.newPage();

  const consoleErrors = [];
  const networkFails  = [];
  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrors.push({ url: page.url(), text: msg.text() });
  });
  page.on('response', r => {
    if (r.status() >= 400) networkFails.push({ url: r.url(), status: r.status() });
  });

  const results = [];
  for (const r of ROUTES) {
    const url = r.literal ? BASE + r.hash : BASE + r.hash;
    const entry = { slug: r.slug, url, ok: false };
    try {
      await page.goto(url, { waitUntil: 'networkidle', timeout: 20000 });
      // Give the hash-router a tick to render
      await page.waitForTimeout(600);
      const shot = path.join(OUT, `${slugify(r.slug)}.png`);
      await page.screenshot({ path: shot, fullPage: true });
      const title   = await page.title();
      const hasApp  = await page.evaluate(() => !!document.getElementById('app'));
      const appText = await page.evaluate(() => {
        const a = document.getElementById('app');
        return a ? a.innerText.slice(0, 200) : '';
      });
      const bodyLen = await page.evaluate(() => document.body.innerText.length);
      const is404   = /Page Not Found/i.test(await page.content());
      entry.ok        = !is404;
      entry.title     = title;
      entry.hasApp    = hasApp;
      entry.appPreview= appText;
      entry.bodyLen   = bodyLen;
      entry.is404     = is404;
      entry.shot      = path.relative(path.resolve(__dirname, '..', '..', '..'), shot);
    } catch (e) {
      entry.error = String(e.message || e);
    }
    results.push(entry);
    console.log(`${entry.ok ? 'OK ' : 'FAIL'}  ${r.slug.padEnd(10)} ${entry.title || entry.error || ''}`);
  }

  const report = { base: BASE, at: new Date().toISOString(), results, consoleErrors, networkFails };
  fs.writeFileSync(path.join(OUT, 'report.json'), JSON.stringify(report, null, 2));
  console.log('\nconsole errors:', consoleErrors.length);
  console.log('network 4xx/5xx:', networkFails.length);
  console.log('report:', path.relative(process.cwd(), path.join(OUT, 'report.json')));

  await browser.close();
  const anyFail = results.some(r => !r.ok);
  process.exit(anyFail ? 1 : 0);
}

main().catch(e => { console.error(e); process.exit(2); });
