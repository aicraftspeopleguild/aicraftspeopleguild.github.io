// ACG-TEST browser terminal.
// Runs ACG-TEST .test.yml files against local or remote targets.
// Supports: local manifest, single-file URLs, pasted YAML, raw GitHub content.

import { runOne, runYaml, parseYAML, makeTotals, verdict, escape, fetchText } from "./runner-core.js";

const SITE_BASE = new URL("..", document.baseURI).href; // /home of the site
const MANIFEST = SITE_BASE + "tests/manifest.json";

const out = document.getElementById("term-output");
const form = document.getElementById("term-form");
const input = document.getElementById("term-input");
const dialog = document.getElementById("paste-dialog");
const pasteForm = document.getElementById("paste-form");
const pasteArea = document.getElementById("paste-area");
const summary = document.getElementById("site-summary");

let lastResults = [];
const history = [];
let historyIdx = -1;

print("ACG-TEST terminal · type 'help' for commands\n");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const line = input.value;
  if (!line.trim()) return;
  history.push(line);
  historyIdx = history.length;
  echo(line);
  input.value = "";
  try {
    await dispatch(line);
  } catch (err) {
    print(`error: ${err.message}\n`, "fail");
  }
  scrollEnd();
});

input.addEventListener("keydown", (e) => {
  if (e.key === "ArrowUp") {
    e.preventDefault();
    if (history.length === 0) return;
    historyIdx = Math.max(0, historyIdx - 1);
    input.value = history[historyIdx] || "";
  } else if (e.key === "ArrowDown") {
    e.preventDefault();
    if (history.length === 0) return;
    historyIdx = Math.min(history.length, historyIdx + 1);
    input.value = history[historyIdx] || "";
  }
});

pasteForm.addEventListener("submit", async (e) => {
  const action = e.submitter && e.submitter.value;
  if (action !== "run") { dialog.close(); return; }
  const text = pasteArea.value;
  dialog.close();
  if (!text.trim()) { print("paste: empty input\n", "skip"); return; }
  print("paste: running...\n");
  try {
    const r = await runYaml(text, document.baseURI);
    renderResult(r);
    lastResults = [r];
    renderLocalSummary(lastResults);
  } catch (err) {
    print(`paste error: ${err.message}\n`, "fail");
  }
});

// ---------- commands ---------- //

async function dispatch(line) {
  const [cmd, ...rest] = tokenize(line);
  const arg = rest.join(" ");
  switch (cmd) {
    case "help":      return cmdHelp();
    case "clear":     return cmdClear();
    case "history":   return cmdHistory();
    case "echo":      return print(arg + "\n");
    case "ls":        return cmdLs();
    case "cat":       return cmdCat(arg);
    case "init":      return cmdInit(arg);
    case "validate":  return cmdValidate(arg);
    case "run":       return cmdRun(arg);
    case "fetch":     return cmdFetch(rest);
    case "target":    return cmdTarget(arg);
    case "paste":     return cmdPaste();
    case "report":    return cmdReport();
    case "papers":    return cmdPapers(rest);
    default:          return print(`unknown command: ${cmd} (try 'help')\n`, "fail");
  }
}

function cmdHelp() {
  print(
`commands

  help                                show this list
  clear                               clear the output buffer
  history                             show command history
  ls                                  list local tests in tests/manifest.json
  cat <path>                          show a file from this site (e.g. tests/index.test.yml)
  run                                 run every local test
  run <url-or-path>                   run a single .test.yml from this site or any URL
  fetch <owner/repo[@ref]> <path>     run a .test.yml from a public GitHub repo
                                      e.g. fetch teslasolar/acg-test tests/index.test.yml
  target <url>                        fetch any HTML and report basic UDT counts
  paste                               open a textarea, paste YAML, run it
  validate <url-or-path>              parse a test file and report shape only
  init <name>                         print a blank .test.yml scaffold
  report                              re-render the last summary
  papers [scan <url>]                 list the site's papers.json, or scan any
                                      HTML URL for an acg-paper frontmatter block

`, "info");
}

async function cmdPapers(rest) {
  const sub = rest[0];
  if (sub === "scan") {
    const url = rest[1];
    if (!url) return print("usage: papers scan <url>\n", "fail");
    try {
      const resolved = resolve(url);
      const text = await fetchText(resolved);
      const m = text.match(/<!--\s*([\s\S]*?)-->/);
      if (!m || !/\bacg-paper\s*:/.test(m[1])) return print("papers scan: no acg-paper frontmatter found\n", "skip");
      const parsed = parseYAML(m[1]);
      const paper = parsed && parsed["acg-paper"] ? parsed["acg-paper"] : null;
      if (!paper) return print("papers scan: frontmatter block present but could not parse\n", "fail");
      print(`papers scan ${resolved}\n`);
      for (const k of ["id", "type", "title", "author", "date", "status", "slug"]) {
        if (paper[k] !== undefined) print(`  ${k.padEnd(9)} ${paper[k]}\n`);
      }
      if (paper.tags) print(`  tags      ${Array.isArray(paper.tags) ? paper.tags.join(", ") : paper.tags}\n`);
      if (paper.abstract) print(`  abstract  ${paper.abstract}\n`);
      const missing = ["title", "author", "type", "abstract"].filter((f) => !paper[f]);
      if (missing.length) print(`  missing required: ${missing.join(", ")}\n`, "fail");
      else print(`  ok — all required fields present\n`, "pass");
    } catch (e) { print(`papers scan: ${e.message}\n`, "fail"); }
    return;
  }
  try {
    const text = await fetchText(SITE_BASE + "papers.json");
    const papers = JSON.parse(text);
    print(`papers.json — ${papers.length} paper${papers.length === 1 ? "" : "s"} indexed\n`);
    for (const p of papers) {
      print(`  ${p.id.padEnd(24)} ${String(p.type).padEnd(14)} ${p.title}\n`, "info");
      if (p.author || p.date) print(`    ${p.author || "?"} · ${p.date || "?"} · tags: ${(p.tags || []).join(", ") || "(none)"}\n`);
    }
  } catch (e) { print(`papers: ${e.message}\n`, "fail"); }
}

function cmdClear() { out.textContent = ""; }

function cmdHistory() {
  if (history.length === 0) { print("(empty)\n"); return; }
  history.forEach((h, i) => print(`${String(i + 1).padStart(3)}  ${h}\n`));
}

async function cmdLs() {
  try {
    const text = await fetchText(MANIFEST);
    const json = JSON.parse(text);
    print(`tests/manifest.json (version ${json.version}) — ${json.tests.length} files\n`);
    for (const t of json.tests) print(`  ${t}\n`);
  } catch (e) { print(`ls: ${e.message}\n`, "fail"); }
}

async function cmdCat(path) {
  if (!path) return print("usage: cat <path>\n", "fail");
  const url = resolve(path);
  try {
    const text = await fetchText(url);
    print(text + (text.endsWith("\n") ? "" : "\n"));
  } catch (e) { print(`cat: ${e.message}\n`, "fail"); }
}

function cmdInit(name) {
  if (!name) return print("usage: init <workflow-or-page-name>\n", "fail");
  const scaffold =
`# tests/${name}.test.yml
test: ${name}
target: <path-or-url>

exists:
  expect: present
  reason: ""

watches:
  - path: ""
    expect: triggered
    reason: ""

guardrails:
  - condition: ""
    reason: ""

secrets:
  - name: ""
    expect: configured
    reason: ""
`;
  print(scaffold);
}

async function cmdValidate(arg) {
  if (!arg) return print("usage: validate <url-or-path>\n", "fail");
  const url = resolve(arg);
  try {
    const text = await fetchText(url);
    const yml = parseYAML(text);
    const wc = (yml.watches || []).length;
    const gc = (yml.guardrails || []).length;
    const sc = (yml.secrets || []).length;
    const tc = (yml.triggers || []).length;
    const missing = [];
    for (const k of ["watches", "guardrails", "secrets", "triggers"]) {
      for (const it of (yml[k] || [])) if (it && !it.reason) missing.push(`${k}[].reason`);
    }
    print(`validate ${url}\n`);
    print(`  test: ${yml.test || "(unset)"}\n`);
    print(`  target: ${yml.target || yml.workflow || "(unset)"}\n`);
    print(`  watches: ${wc}  guardrails: ${gc}  secrets: ${sc}  triggers: ${tc}\n`);
    if (missing.length) print(`  missing reason on: ${missing.join(", ")}\n`, "fail");
    else print(`  ok — every expectation has a reason\n`, "pass");
  } catch (e) { print(`validate: ${e.message}\n`, "fail"); }
}

async function cmdRun(arg) {
  if (!arg) {
    // run all from manifest
    try {
      const text = await fetchText(MANIFEST);
      const json = JSON.parse(text);
      lastResults = [];
      for (const t of json.tests) {
        const r = await runOne(SITE_BASE + t);
        renderResult(r);
        lastResults.push(r);
      }
      renderLocalSummary(lastResults);
    } catch (e) { print(`run: ${e.message}\n`, "fail"); }
    return;
  }
  const url = resolve(arg);
  try {
    const r = await runOne(url);
    renderResult(r);
    lastResults = [r];
    renderLocalSummary(lastResults);
  } catch (e) { print(`run: ${e.message}\n`, "fail"); }
}

async function cmdFetch(parts) {
  if (parts.length < 2) return print("usage: fetch <owner/repo[@ref]> <path>\n", "fail");
  const [repoSpec, ...pathParts] = parts;
  const path = pathParts.join(" ");
  let owner, repo, ref = "main";
  const m = repoSpec.match(/^([^/]+)\/([^@]+)(?:@(.+))?$/);
  if (!m) return print("fetch: repo must be owner/repo[@ref]\n", "fail");
  [, owner, repo] = m; if (m[3]) ref = m[3];
  const url = `https://raw.githubusercontent.com/${owner}/${repo}/${ref}/${path}`;
  print(`fetch ${url}\n`);
  try {
    const r = await runOne(url);
    renderResult(r);
    lastResults = [r];
    renderLocalSummary(lastResults);
  } catch (e) { print(`fetch: ${e.message}\n`, "fail"); }
}

async function cmdTarget(url) {
  if (!url) return print("usage: target <url>\n", "fail");
  try {
    const text = await fetchText(url);
    const doc = new DOMParser().parseFromString(text, "text/html");
    const counts = {};
    for (const t of ["udt-expectation", "udt-eventtrigger", "udt-pathwatch", "udt-guardrail", "udt-secret", "udt-notification", "udt-field", "udt-workflowtest"]) {
      counts[t] = doc.querySelectorAll(t).length;
    }
    print(`target ${url}\n`);
    print(`  title: ${doc.title || "(no title)"}\n`);
    print(`  h1 count: ${doc.querySelectorAll("h1").length}\n`);
    let total = 0;
    for (const [k, v] of Object.entries(counts)) {
      print(`  ${k.padEnd(22)} ${v}\n`);
      total += v;
    }
    print(`  total UDT elements: ${total}\n`, total > 0 ? "pass" : "skip");
  } catch (e) { print(`target: ${e.message}\n`, "fail"); }
}

function cmdPaste() {
  if (typeof dialog.showModal !== "function") {
    print("paste: <dialog> not supported in this browser\n", "fail");
    return;
  }
  pasteArea.value = "";
  dialog.showModal();
  setTimeout(() => pasteArea.focus(), 0);
}

function cmdReport() {
  if (lastResults.length === 0) { print("report: nothing to show — run something first\n", "skip"); return; }
  for (const r of lastResults) renderResult(r);
  renderLocalSummary(lastResults);
}

// ---------- helpers ---------- //

function resolve(arg) {
  if (/^https?:\/\//i.test(arg)) return arg;
  return SITE_BASE + arg.replace(/^\/+/, "");
}

function tokenize(line) {
  const out = [];
  let buf = "", inStr = null;
  for (let k = 0; k < line.length; k++) {
    const c = line[k];
    if (inStr) {
      if (c === inStr) { inStr = null; continue; }
      buf += c;
    } else if (c === '"' || c === "'") {
      inStr = c;
    } else if (c === " " || c === "\t") {
      if (buf) { out.push(buf); buf = ""; }
    } else {
      buf += c;
    }
  }
  if (buf) out.push(buf);
  return out;
}

function echo(line) { print(`acg-test \u276F ${line}\n`, "echo"); }

function print(text, kind) {
  const span = document.createElement("span");
  if (kind) span.className = `t-${kind}`;
  span.textContent = text;
  out.appendChild(span);
  scrollEnd();
}

function scrollEnd() { out.scrollTop = out.scrollHeight; }

function renderResult(r) {
  const verdictKind = r.totals.failed > 0 ? "fail" : (r.totals.skipped > 0 && r.totals.passed === 0 ? "skip" : "pass");
  const tag = verdictKind === "fail" ? "FAIL" : (verdictKind === "skip" ? "PARTIAL" : "PASS");
  print(`\n[${tag}] ${r.name}\n`, verdictKind);
  print(`  file: ${r.file}\n`, "info");
  print(`  target: ${r.target || "(none)"}\n`, "info");
  print(`  totals: ${r.totals.passed}p / ${r.totals.failed}f / ${r.totals.skipped}s\n`, "info");
  for (const x of r.results) {
    const mark = x.result === "pass" ? "\u2713" : x.result === "fail" ? "\u2717" : "\u25CB";
    const reason = x.reason ? ` — ${x.reason}` : "";
    const detail = x.result === "fail" ? `   (expected ${x.expected}, got ${x.actual})` : "";
    print(`  ${mark} ${x.name}${reason}\n`, x.result);
    if (detail) print(`${detail}\n`, "fail");
  }
}

function renderLocalSummary(results) {
  if (!summary) return;
  const totals = results.reduce((acc, r) => {
    acc.passed += r.totals.passed; acc.failed += r.totals.failed; acc.skipped += r.totals.skipped;
    return acc;
  }, makeTotals());
  const v = verdict(totals);
  summary.classList.remove("verdict-green", "verdict-red", "verdict-yellow");
  summary.classList.add(`verdict-${v}`);
  summary.innerHTML = `
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

input.focus();
