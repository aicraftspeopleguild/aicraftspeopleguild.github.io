// ═══ autofire · read URL #action + self-find back nav target ═══
import { log } from './log.js';
import { runCmd } from './cmd.js';

// Self-find the "back" destination. Priority:
//   1. explicit ?back= in URL hash
//   2. document.referrer (set by GitHub's README link-through)
//   3. stored last-source in localStorage
// Result is persisted so repeat visits re-use the same source.
export function findBack() {
  const q = new URLSearchParams(location.hash.slice(1));
  const explicit = q.get('back');
  if (explicit) { localStorage.setItem('acg_back', explicit); return explicit; }

  const ref = document.referrer;
  if (ref && /github\.com|github\.io/.test(ref) && !ref.includes('/control-deck/')) {
    localStorage.setItem('acg_back', ref);
    return ref;
  }

  return localStorage.getItem('acg_back') || '';
}

export function maybeReturn() {
  const back = findBack();
  if (!back) return;
  let n = 3;
  const tick = () => {
    log(`↩ returning in ${n}s — ${back.slice(0, 60)}`, 'info');
    if (n-- <= 0) location.href = back;
    else setTimeout(tick, 1000);
  };
  tick();
}

// ── parse #action= and fire the matching action once the DOM is ready
export function bootAutofire() {
  const q = new URLSearchParams(location.hash.slice(1));
  const action = q.get('action');
  if (!action) return;
  const path  = q.get('path')  || '';
  const value = q.get('value') || '';

  const plain = {
    'bump-heartbeat': 'cmd:bump-heartbeat',
    'rebuild-svgs':   'cmd:rebuild-svgs',
    'rebuild-api':    'cmd:rebuild-api',
    'clear-faults':   'cmd:clear-faults',
  };
  if (plain[action]) {
    log('auto-firing #action=' + action, 'ok');
    setTimeout(() => runCmd(plain[action], 'fired from README'), 500);
    return;
  }
  if (action === 'tag-write' && path && value) {
    const tp = document.getElementById('tag-path');
    const tv = document.getElementById('tag-value');
    if (tp) tp.value = path;
    if (tv) tv.value = value;
    log(`auto-firing tag-write ${path}=${value}`, 'ok');
    setTimeout(() => runCmd(`cmd:tag-write path=${path} value=${value}`, 'fired from README'), 500);
    return;
  }
  log('unknown #action=' + action, 'err');
}

// ── render back chip (manual escape hatch)
export function renderBackChip() {
  const back = findBack();
  if (!back) return;
  const el = document.getElementById('back-chip');
  if (!el) return;
  el.href = back;
  el.textContent = '↩ ' + back.replace(/^https?:\/\//, '').slice(0, 36);
  el.style.display = '';
}
