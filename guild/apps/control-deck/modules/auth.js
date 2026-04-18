// ═══ auth · PAT storage + auth-chip rendering ═══
import { log } from './log.js';

const KEY = 'acg_gh_pat';

export function loadTok() {
  return localStorage.getItem(KEY) || '';
}

export function saveTok(v) {
  if (v) localStorage.setItem(KEY, v);
  else   localStorage.removeItem(KEY);
  renderAuth();
}

export function renderAuth() {
  const chip = document.getElementById('auth-chip');
  const text = document.getElementById('auth-text');
  if (!chip || !text) return;
  if (loadTok()) {
    chip.className = 'auth on';
    text.textContent = 'token loaded · direct writes enabled';
  } else {
    chip.className = 'auth off';
    text.textContent = 'no token · uses pre-filled issue fallback';
  }
}

export function bootAuth() {
  const input = document.getElementById('tok');
  if (input) {
    input.value = loadTok();
    input.addEventListener('change', e => saveTok(e.target.value.trim()));
  }
  renderAuth();
  log('auth: ' + (loadTok() ? 'authed' : 'anonymous'), loadTok() ? 'ok' : 'info');
}

// ── thin GitHub REST helper
export async function gh(method, path, body) {
  const tok = loadTok();
  if (!tok) throw new Error('no token · click "open pre-filled issue" instead');
  const r = await fetch('https://api.github.com' + path, {
    method,
    headers: {
      'Authorization': 'Bearer ' + tok,
      'Accept': 'application/vnd.github+json',
      'Content-Type': 'application/json',
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!r.ok) throw new Error('github ' + r.status + ': ' + (await r.text()).slice(0, 120));
  return r.json();
}
