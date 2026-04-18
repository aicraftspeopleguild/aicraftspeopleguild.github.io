/* ═══════════════════════════════════════════════════════
   ui.js — DOM refs, output helpers, fetch utility,
           and tag-tree traversal helpers
   ═══════════════════════════════════════════════════════ */
'use strict';

/* ── DOM refs ── */
const out   = document.getElementById('output');
const input = document.getElementById('cmd-input');
const hint  = document.getElementById('hint');

/* ── HTML escaping ── */
function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

/* ── Output primitives ── */
function line(html, cls = 'line') {
  const d = document.createElement('div');
  d.className = `line ${cls}`;
  d.innerHTML = html;
  out.appendChild(d);
  out.scrollTop = out.scrollHeight;
  return d;
}

function echoCmd(cmd) {
  const d = document.createElement('div');
  d.className = 'line line-cmd';
  d.innerHTML = `<span class="ps-echo">guild@acg</span><span class="sep-echo">:~$ </span>${esc(cmd)}`;
  out.appendChild(d);
  out.scrollTop = out.scrollHeight;
}

function blank() { line(''); }

/** Render a key/value pair with optional value colour class. */
function kv(k, v, vClass = 'line-val') {
  line(`  <span class="line-key">${esc(k)}</span>  <span class="${vClass}">${esc(v)}</span>`);
}

/** Show an animated spinner; returns a function that removes it. */
function spinner() {
  const d = line('  <span class="spin">⠋</span> fetching…', 'line-dim');
  return () => d.remove();
}

/* ── Fetch helper ── */
async function apiFetch(url) {
  const r = await fetch(url, { cache: 'no-cache' });
  if (!r.ok) throw new Error(`HTTP ${r.status} ${r.statusText}`);
  return r.json();
}

/* ── Tag-tree helpers ─────────────────────────────────
   These mirror the ACG runtime tag bus structure where
   leaf nodes carry { value, quality, updated_at }.      */

/** Traverse a nested tag object by dot-separated path. */
function navPath(obj, dotPath) {
  return dotPath.split('.').reduce((node, key) => {
    if (node == null || typeof node !== 'object') return undefined;
    return node[key];
  }, obj);
}

/** Flatten a nested tag tree into [{path, value, quality, …}]. */
function flattenTags(obj, prefix = '') {
  const results = [];
  for (const [k, v] of Object.entries(obj || {})) {
    const fullKey = prefix ? `${prefix}.${k}` : k;
    if (v && typeof v === 'object' && 'value' in v) {
      results.push({ path: fullKey, ...v });
    } else if (v && typeof v === 'object') {
      results.push(...flattenTags(v, fullKey));
    }
  }
  return results;
}
