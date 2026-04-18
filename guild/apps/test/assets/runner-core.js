// ACG-TEST runner core.
// Pure functions for parsing test YAML and running checks.
// Imported by test-runner.js (page bootstrap) and terminal.js (interactive use).

// ---------- minimal YAML subset parser ---------- //

export function parseYAML(text) {
  const raw = text.replace(/\r\n/g, "\n").split("\n");
  const lines = [];
  for (const line of raw) {
    const noComment = stripComment(line).replace(/\s+$/, "");
    if (noComment.trim() === "") continue;
    lines.push(noComment);
  }

  let i = 0;
  const indentOf = (l) => l.match(/^ */)[0].length;

  function parseBlock(parentIndent) {
    if (i >= lines.length) return null;
    const first = lines[i];
    const curIndent = indentOf(first);
    if (curIndent <= parentIndent) return null;

    if (first.slice(curIndent).startsWith("- ")) {
      const arr = [];
      while (i < lines.length) {
        const line = lines[i];
        const li = indentOf(line);
        if (li < curIndent) break;
        if (li !== curIndent || !line.slice(li).startsWith("- ")) break;

        const rest = line.slice(li + 2);
        const m = rest.match(/^([^:]+):\s*(.*)$/);
        if (m) {
          lines[i] = " ".repeat(li + 2) + rest;
          const val = parseBlock(li + 1);
          arr.push(val);
        } else {
          arr.push(parseScalar(rest));
          i++;
        }
      }
      return arr;
    }

    const obj = {};
    while (i < lines.length) {
      const line = lines[i];
      const li = indentOf(line);
      if (li < curIndent) break;
      if (li > curIndent) { i++; continue; }
      const content = line.slice(li);
      const m = content.match(/^([^:]+):\s*(.*)$/);
      if (!m) { i++; continue; }
      const key = m[1].trim();
      const val = m[2].trim();
      i++;
      if (val === ">" || val === "|") {
        obj[key] = readBlockScalar(val === "|", curIndent);
      } else if (val === "") {
        const child = parseBlock(curIndent);
        obj[key] = child === null ? null : child;
      } else {
        obj[key] = parseScalar(val);
      }
    }
    return obj;
  }

  function readBlockScalar(literal, parentIndent) {
    const parts = [];
    let blockIndent = -1;
    while (i < lines.length) {
      const line = lines[i];
      const li = indentOf(line);
      if (li <= parentIndent) break;
      if (blockIndent === -1) blockIndent = li;
      parts.push(line.slice(blockIndent));
      i++;
    }
    if (literal) return parts.join("\n");
    // folded: blank line → newline, otherwise join with space
    let folded = "";
    for (let k = 0; k < parts.length; k++) {
      const p = parts[k];
      if (p.trim() === "") folded += "\n";
      else folded += (folded && !folded.endsWith("\n") ? " " : "") + p.trim();
    }
    return folded.trim();
  }

  return parseBlock(-1);
}

function stripComment(line) {
  let out = "";
  let inStr = null;
  for (let k = 0; k < line.length; k++) {
    const c = line[k];
    if (inStr) {
      out += c;
      if (c === inStr && line[k - 1] !== "\\") inStr = null;
    } else if (c === '"' || c === "'") {
      inStr = c;
      out += c;
    } else if (c === "#") {
      break;
    } else {
      out += c;
    }
  }
  return out;
}

function parseScalar(s) {
  if (s === "") return null;
  if (s.startsWith("[") && s.endsWith("]")) {
    const inner = s.slice(1, -1).trim();
    if (inner === "") return [];
    return splitTopLevel(inner, ",").map(x => parseScalar(x.trim()));
  }
  if ((s.startsWith('"') && s.endsWith('"')) || (s.startsWith("'") && s.endsWith("'"))) {
    return s.slice(1, -1);
  }
  if (/^-?\d+$/.test(s)) return parseInt(s, 10);
  if (/^-?\d*\.\d+$/.test(s)) return parseFloat(s);
  if (s === "true") return true;
  if (s === "false") return false;
  if (s === "null" || s === "~") return null;
  return s;
}

function splitTopLevel(s, sep) {
  const out = [];
  let depth = 0, buf = "", inStr = null;
  for (let k = 0; k < s.length; k++) {
    const c = s[k];
    if (inStr) { buf += c; if (c === inStr) inStr = null; continue; }
    if (c === '"' || c === "'") { inStr = c; buf += c; continue; }
    if (c === "[" || c === "{") depth++;
    if (c === "]" || c === "}") depth--;
    if (c === sep && depth === 0) { out.push(buf); buf = ""; continue; }
    buf += c;
  }
  if (buf.trim() !== "") out.push(buf);
  return out;
}

// ---------- helpers ---------- //

export function makeTotals() { return { passed: 0, failed: 0, skipped: 0 }; }

export function tally(totals, result) {
  if (result === "pass") totals.passed++;
  else if (result === "fail") totals.failed++;
  else totals.skipped++;
}

export function verdict(totals) {
  if (totals.failed > 0) return "red";
  if (totals.skipped > 0) return "yellow";
  return "green";
}

export function escape(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

export function looksLikeSelector(s) {
  if (!s || typeof s !== "string") return false;
  return /^[a-zA-Z0-9\[\].#:>*~\s\-_="'()]+$/.test(s) && /[.#\[:a-zA-Z]/.test(s);
}

// ---------- runner ---------- //

export async function fetchText(url) {
  const r = await fetch(url, { cache: "no-store" });
  if (!r.ok) throw new Error(`fetch ${url} → ${r.status}`);
  return await r.text();
}

export async function fetchDoc(url) {
  const text = await fetchText(url);
  return new DOMParser().parseFromString(text, "text/html");
}

function resolveAgainst(testUrl, target) {
  try { return new URL(target, testUrl).href; }
  catch (_) { return target; }
}

export async function runOne(testUrl) {
  const out = { file: testUrl, name: testUrl, target: null, results: [], totals: makeTotals() };
  let yml;
  try {
    yml = parseYAML(await fetchText(testUrl));
  } catch (e) {
    out.results.push({ name: "load test file", result: "fail", reason: "test file could not be loaded: " + e.message, expected: "present", actual: "missing" });
    out.totals.failed++;
    return out;
  }
  return runParsed(yml, testUrl, out);
}

export async function runYaml(yamlText, sourceUrl = window.location.href) {
  const out = { file: sourceUrl, name: sourceUrl, target: null, results: [], totals: makeTotals() };
  let yml;
  try {
    yml = parseYAML(yamlText);
  } catch (e) {
    out.results.push({ name: "parse test yaml", result: "fail", reason: "could not parse YAML: " + e.message, expected: "valid yaml", actual: "invalid" });
    out.totals.failed++;
    return out;
  }
  return runParsed(yml, sourceUrl, out);
}

async function runParsed(yml, sourceUrl, out) {
  out.name = yml.test || sourceUrl;
  out.target = yml.target || yml.workflow || null;

  const targetUrl = out.target ? resolveAgainst(sourceUrl, out.target) : null;

  if (yml.exists) {
    const r = await checkExists(yml.exists, out.target, targetUrl);
    out.results.push(r);
    tally(out.totals, r.result);
  }

  let doc = null;
  if (targetUrl && /\.html?$/.test(out.target)) {
    try { doc = await fetchDoc(targetUrl); } catch (_) { doc = null; }
  }

  for (const w of (yml.watches || [])) {
    const r = checkWatch(w, doc);
    out.results.push(r);
    tally(out.totals, r.result);
  }

  for (const g of (yml.guardrails || [])) {
    const r = checkGuardrail(g, doc);
    out.results.push(r);
    tally(out.totals, r.result);
  }

  for (const s of (yml.secrets || [])) {
    const r = await checkSecret(s, sourceUrl);
    out.results.push(r);
    tally(out.totals, r.result);
  }

  for (const t of (yml.triggers || [])) {
    out.results.push({
      name: `trigger: ${t.event}`,
      result: "skip",
      reason: t.reason || "workflow trigger requires runtime check",
      expected: t.expect,
      actual: "needs runtime check",
    });
    out.totals.skipped++;
  }

  if (yml.notification) {
    out.results.push({
      name: "notification shape",
      result: "skip",
      reason: "notification shape requires runtime check",
      expected: "present",
      actual: "needs runtime check",
    });
    out.totals.skipped++;
  }

  // Optional: output[] — generated files that must exist relative to sourceUrl.
  for (const o of (yml.output || [])) {
    const r = await checkOutputFile(o, sourceUrl);
    out.results.push(r);
    tally(out.totals, r.result);
  }

  // Optional: frontmatter.required[] / frontmatter.auto-filled[] — workflow-runtime items.
  if (yml.frontmatter) {
    for (const group of ["required", "auto-filled", "autofilled", "auto_filled"]) {
      for (const f of (yml.frontmatter[group] || [])) {
        out.results.push({
          name: `frontmatter.${group}: ${f.field}`,
          result: "skip",
          reason: f.reason || "frontmatter rule requires runtime check",
          expected: f.expect || "configured",
          actual: "needs runtime check",
        });
        out.totals.skipped++;
      }
    }
  }

  return out;
}

async function checkOutputFile(o, sourceUrl) {
  const name = `output: ${o.file}`;
  if (!o.file) {
    return { name, result: "fail", reason: o.reason || "", expected: "present", actual: "missing file field" };
  }
  try {
    const url = resolveAgainst(sourceUrl, o.file);
    const r = await fetch(url, { method: "GET", cache: "no-store" });
    if (r.ok) return { name, result: "pass", reason: o.reason || "", expected: "present", actual: "present" };
    return { name, result: "fail", reason: o.reason || "", expected: "present", actual: `${r.status}` };
  } catch (_) {
    return { name, result: "fail", reason: o.reason || "", expected: "present", actual: "unreachable" };
  }
}

async function checkExists(exists, targetPath, targetUrl) {
  const name = `exists: ${targetPath || "(unset)"}`;
  if (!targetUrl) {
    return { name, result: "fail", reason: exists.reason || "", expected: "target set", actual: "missing target" };
  }
  try {
    const r = await fetch(targetUrl, { method: "GET", cache: "no-store" });
    if (r.ok) return { name, result: "pass", reason: exists.reason || "", expected: "present", actual: "present" };
    return { name, result: "fail", reason: exists.reason || "", expected: "present", actual: `${r.status}` };
  } catch (_) {
    return { name, result: "fail", reason: exists.reason || "", expected: "present", actual: "unreachable" };
  }
}

function checkWatch(watch, doc) {
  const name = `watch: ${watch.path}`;
  const expect = watch.expect || "triggered";
  if (!doc) {
    return { name, result: "skip", reason: watch.reason || "", expected: expect, actual: "no DOM available" };
  }
  let found;
  try { found = doc.querySelector(watch.path) !== null; }
  catch (e) { return { name, result: "fail", reason: watch.reason || "", expected: expect, actual: "invalid selector: " + e.message }; }
  const shouldMatch = expect === "triggered";
  const ok = found === shouldMatch;
  return {
    name,
    result: ok ? "pass" : "fail",
    reason: watch.reason || "",
    expected: expect,
    actual: found ? "triggered" : "not triggered",
  };
}

function checkGuardrail(g, doc) {
  const name = `guardrail: ${g.condition}`;
  const selector = looksLikeSelector(g.condition) ? g.condition : null;
  if (selector && doc) {
    let found;
    try { found = doc.querySelector(selector) !== null; }
    catch (_) { return { name, result: "skip", reason: g.reason || "", expected: "not triggered", actual: "invalid selector" }; }
    return {
      name,
      result: found ? "fail" : "pass",
      reason: g.reason || "",
      expected: "not triggered",
      actual: found ? "triggered" : "not triggered",
    };
  }
  return { name, result: "skip", reason: g.reason || "", expected: "not triggered", actual: "needs runtime check" };
}

async function checkSecret(s, sourceUrl) {
  const name = `secret/asset: ${s.name}`;
  const isFile = typeof s.name === "string" && /\.[a-z0-9]+$/i.test(s.name);
  if (!isFile) {
    return { name, result: "skip", reason: s.reason || "", expected: "configured", actual: "needs runtime check" };
  }
  try {
    const url = resolveAgainst(sourceUrl, s.name);
    const r = await fetch(url, { method: "GET", cache: "no-store" });
    if (r.ok) return { name, result: "pass", reason: s.reason || "", expected: "configured", actual: "configured" };
    return { name, result: "fail", reason: s.reason || "", expected: "configured", actual: `${r.status}` };
  } catch (_) {
    return { name, result: "fail", reason: s.reason || "", expected: "configured", actual: "unreachable" };
  }
}
