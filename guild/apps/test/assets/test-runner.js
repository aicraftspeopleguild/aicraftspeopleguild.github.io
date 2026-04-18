// ACG-TEST page bootstrap.
// Loads tests/manifest.json, runs every test, renders into mount points
// (#site-summary, #test-list, #process-steps) on whichever page hosts them.

import { runOne, makeTotals, verdict, escape } from "./runner-core.js";

async function loadManifest() {
  const candidates = ["tests/manifest.json", "../tests/manifest.json"];
  for (const url of candidates) {
    try {
      const r = await fetch(url, { cache: "no-store" });
      if (r.ok) return { base: url.replace("tests/manifest.json", ""), manifest: await r.json() };
    } catch (_) {}
  }
  throw new Error("tests/manifest.json not found");
}

function renderSummary(el, results) {
  const totals = results.reduce((acc, r) => {
    const t = r.totals;
    acc.passed += t.passed; acc.failed += t.failed; acc.skipped += t.skipped;
    return acc;
  }, makeTotals());
  const v = verdict(totals);
  el.classList.remove("verdict-green", "verdict-red", "verdict-yellow");
  el.classList.add(`verdict-${v}`);

  el.innerHTML = `
    <div class="totals">
      <span class="p">${totals.passed} passed</span>
      <span class="f">${totals.failed} failed</span>
      <span class="s">${totals.skipped} skipped</span>
      <span>across ${results.length} test file${results.length === 1 ? "" : "s"}</span>
    </div>
    <ul>
      ${results.map(r => `
        <li class="${r.totals.failed > 0 ? "fail" : r.totals.skipped > 0 ? "skip" : "pass"}">
          <strong>${escape(r.name)}</strong>
          <span class="reason">${r.totals.passed}p / ${r.totals.failed}f / ${r.totals.skipped}s</span>
        </li>
      `).join("")}
    </ul>
  `;
}

function renderList(el, results) {
  el.innerHTML = results.map(r => `
    <details ${r.totals.failed > 0 ? "open" : ""}>
      <summary>
        ${escape(r.name)}
        <span class="badge ${r.totals.failed ? "fail" : r.totals.skipped ? "skip" : "pass"}">
          ${r.totals.failed ? "FAIL" : r.totals.skipped ? "PARTIAL" : "PASS"}
        </span>
      </summary>
      <div class="body">
        <p class="quiet">${escape(r.file)} · target: ${escape(r.target || "(none)")}</p>
        <ul class="summary">
          ${r.results.map(x => `
            <li class="${x.result}">
              <strong>${escape(x.name)}</strong>
              <span class="reason">&mdash; ${escape(x.reason || "")}</span>
              ${x.result === "fail" ? `<div class="reason">expected ${escape(x.expected)} &middot; got ${escape(x.actual)}</div>` : ""}
            </li>
          `).join("")}
        </ul>
      </div>
    </details>
  `).join("");
}

function renderProcess(el, fileResults) {
  if (!el) return;
  const totalFail = fileResults.reduce((n, r) => n + r.totals.failed, 0);
  const totalPass = fileResults.reduce((n, r) => n + r.totals.passed, 0);
  const anyExists = fileResults.some(r => r.results.some(x => x.name.startsWith("exists:") && x.result === "pass"));
  const mark = (key, state) => {
    const li = el.querySelector(`[data-step="${key}"] .r`);
    if (!li) return;
    li.classList.remove("pass", "fail", "skip");
    li.classList.add(state);
    li.textContent = state;
  };
  mark("scaffold", "pass");
  mark("fail", totalFail === 0 ? "pass" : "fail");
  mark("write", anyExists ? "pass" : "fail");
  mark("pass", totalFail === 0 && totalPass > 0 ? "pass" : totalFail > 0 ? "fail" : "skip");
  mark("commit", totalFail === 0 && totalPass > 0 ? "pass" : "skip");
}

async function main() {
  const summaryEl = document.getElementById("site-summary");
  const listEl = document.getElementById("test-list");
  const processEl = document.getElementById("process-steps");
  if (!summaryEl && !listEl && !processEl) return;

  let base, manifest;
  try {
    ({ base, manifest } = await loadManifest());
  } catch (e) {
    if (summaryEl) summaryEl.textContent = "manifest not found: " + e.message;
    return;
  }

  const results = [];
  for (const path of manifest.tests) {
    const r = await runOne(base + path);
    results.push(r);
  }

  if (summaryEl) renderSummary(summaryEl, results);
  if (listEl) renderList(listEl, results);
  if (processEl) renderProcess(processEl, results);
}

main();
