/* ═══════════════════════════════════════════════════════
   input.js — command history, parser, tab completion,
              keyboard/input event handlers, and boot.
   Depends on: ui.js (out/input/hint/line/blank/echoCmd/esc),
               commands.js (COMMANDS), config.js (ENDPOINTS)
   ═══════════════════════════════════════════════════════ */
'use strict';

/* ── history state ── */
const history   = [];
let   hIdx      = -1;
let   savedDraft = '';

/* ── command parser ──────────────────────────────────────
   "tag:read tag=enterprise.paperCount prefix=enterprise"
   → { cmd: 'tag:read', args: { tag: '...', prefix: '...' } }  */
function parseCmd(raw) {
  const parts = raw.trim().split(/\s+/);
  const cmd   = parts[0];
  const args  = {};
  for (const p of parts.slice(1)) {
    const [k, ...vParts] = p.split('=');
    if (vParts.length) args[k] = vParts.join('=');
    else (args._rest = args._rest || []).push(k);
  }
  return { cmd, args };
}

/* ── tab completion ── */
const ALL_CMDS = Object.keys(COMMANDS).sort();

function updateHint(val) {
  if (!val.trim()) { hint.textContent = ''; return; }
  const { cmd } = parseCmd(val);
  const matches = ALL_CMDS.filter(c => c.startsWith(cmd));
  if (matches.length === 1 && matches[0] !== cmd) {
    hint.innerHTML = `<span style="color:var(--dim)">→ ${esc(matches[0])}</span>`;
  } else if (matches.length > 1 && !cmd.includes(':')) {
    hint.innerHTML = matches.map(m => `<span style="color:var(--dim)">${esc(m)}</span>`).join('  ');
  } else {
    hint.textContent = '';
  }
}

/* ── keyboard handler ────────────────────────────────── */
input.addEventListener('keydown', async (e) => {
  if (e.key === 'Enter') {
    const raw = input.value.trim();
    input.value = '';
    hint.textContent = '';
    if (!raw) return;

    history.unshift(raw);
    hIdx      = -1;
    savedDraft = '';

    echoCmd(raw);
    const { cmd, args } = parseCmd(raw);
    const handler = COMMANDS[cmd];
    if (handler) {
      input.disabled = true;
      try   { await handler(args); }
      finally { input.disabled = false; input.focus(); }
    } else {
      line(`  <span class="line-err">✗ unknown command: ${esc(cmd)}</span>`);
      line('  <span class="line-dim">Type <span class="line-key">help</span> to see available commands.</span>');
      blank();
    }

  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    if (hIdx === -1) savedDraft = input.value;
    if (hIdx < history.length - 1) { hIdx++; input.value = history[hIdx]; }
    updateHint(input.value);

  } else if (e.key === 'ArrowDown') {
    e.preventDefault();
    if (hIdx > 0)       { hIdx--; input.value = history[hIdx]; }
    else if (hIdx === 0) { hIdx = -1; input.value = savedDraft; }
    updateHint(input.value);

  } else if (e.key === 'Tab') {
    e.preventDefault();
    const val = input.value.trim();
    if (!val) return;
    const matches = ALL_CMDS.filter(c => c.startsWith(val));
    if (matches.length === 1) {
      input.value = matches[0] + ' ';
      hint.textContent = '';
    } else if (matches.length > 1) {
      hint.innerHTML = matches.map(m => `<span style="color:var(--blue)">${esc(m)}</span>`).join('  ');
    }

  } else if (e.key === 'l' && e.ctrlKey) {
    e.preventDefault();
    out.innerHTML = '';
  }
});

input.addEventListener('input', () => updateHint(input.value));

/* click anywhere → focus input */
document.addEventListener('click', () => input.focus());

/* ── boot sequence ───────────────────────────────────── */
async function boot() {
  const lines = [
    '<span class="line-dim">AI Craftspeople Guild — ISA-95 live control-plane</span>',
    '<span class="line-dim">static JSON API · browser P2P mesh · Konomi UDT engine</span>',
    '',
    '<span class="line-ok">⚒  ACG Guild Terminal v1.0</span>  <span class="line-dim">— type <span class="line-key">help</span> to begin</span>',
    '',
  ];
  for (const l of lines) {
    line(l);
    await new Promise(r => setTimeout(r, 60));
  }
  input.focus();
}

boot();

/* ── public bridge — lets terminal-chat.js register
      extra commands and write into the same output  ── */
window.ACG_TERMINAL = { COMMANDS, line, blank, kv, esc, echoCmd, ENDPOINTS };
