// ═══ cmd · load ControlAction UDT instances + render buttons + dispatch ═══
import { log } from './log.js';
import { loadTok, gh } from './auth.js';
import { refreshSvg } from './preview.js';
import { maybeReturn } from './autofire.js';

// Self-detect which GH repo we're running on so the same code works from
// teslasolar.github.io/aicraftspeopleguild.github.io/ *and* from the org
// host aicraftspeopleguild.github.io/. Override via ?repo=owner/name in
// the hash for local dev.
function detectRepo() {
  const q = new URLSearchParams(location.hash.slice(1));
  const override = q.get('repo');
  if (override && /^[\w.-]+\/[\w.-]+$/.test(override)) return override;
  const host = location.hostname;
  // github pages: <owner>.github.io
  if (host.endsWith('.github.io')) {
    const owner = host.replace(/\.github\.io$/, '');
    const first = (location.pathname.split('/').filter(Boolean)[0]) || '';
    // project page: /<repo>/...
    if (first.endsWith('.github.io') || /^[\w.-]+$/.test(first)) return `${owner}/${first || host}`;
    // user/org page: repo name == hostname
    return `${owner}/${host}`;
  }
  // localhost / unknown → safe default
  return 'teslasolar/aicraftspeopleguild.github.io';
}

export const REPO = detectRepo();

export function issueUrl(title, body = '', labels = 'cmd') {
  const q = new URLSearchParams({ title, body, labels });
  return `https://github.com/${REPO}/issues/new?${q.toString()}`;
}

export async function runCmd(title, body = '', opts = {}) {
  const tok = loadTok();
  if (!tok) {
    window.open(issueUrl(title, body), '_blank');
    log('opened issue form · ' + title, 'info');
    return { ok: false, reason: 'anonymous' };
  }
  try {
    log('POSTing issue ' + title + ' …', 'info');
    const res = await gh('POST', `/repos/${REPO}/issues`, { title, body, labels: ['cmd'] });
    log('✓ issue #' + res.number + ' queued — workflow runs next', 'ok');
    setTimeout(refreshSvg, 12000);
    setTimeout(refreshSvg, 45000);
    if (opts.autoReturn !== false) maybeReturn();
    return { ok: true, issue: res.number };
  } catch (e) {
    log('✗ ' + e.message, 'err');
    return { ok: false, error: e.message };
  }
}

// ── load the ControlAction manifest + render buttons
export async function bootActions() {
  let manifest;
  try {
    manifest = await fetch('./actions/index.json', { cache: 'no-store' }).then(r => r.json());
  } catch {
    log('could not load actions/index.json', 'err');
    return;
  }
  const host = document.getElementById('action-buttons');
  if (!host) return;
  host.innerHTML = '';
  const actions = [];
  for (const file of manifest.actions || []) {
    try {
      const doc = await fetch('./actions/' + file, { cache: 'no-store' }).then(r => r.json());
      actions.push(doc.parameters);
    } catch {}
  }
  actions.sort((a, b) => (a.order || 0) - (b.order || 0));
  // 2-per-row layout
  for (let i = 0; i < actions.length; i += 2) {
    const row = document.createElement('div');
    row.className = 'row';
    for (const p of actions.slice(i, i + 2)) {
      const b = document.createElement('button');
      if (p.color) b.className = p.color;
      b.textContent = p.label;
      b.addEventListener('click', () => runCmd(p.title, p.body || ''));
      row.appendChild(b);
    }
    host.appendChild(row);
  }
  log(`loaded ${actions.length} ControlAction(s)`, 'ok');
}

// ── write-any-tag form wiring
export function bootWriteForm() {
  const w = document.getElementById('write-direct');
  const i = document.getElementById('write-issue');
  if (!w || !i) return;
  w.addEventListener('click', async () => {
    const path = document.getElementById('tag-path').value.trim();
    const value = document.getElementById('tag-value').value;
    const type  = document.getElementById('tag-type').value;
    const qlty  = document.getElementById('tag-quality').value;
    const desc  = document.getElementById('tag-desc').value;
    if (!path) return log('path required', 'err');
    await runCmd(
      `cmd:tag-write path=${path} value=${value}`,
      desc || `type=${type} quality=${qlty}`,
    );
  });
  i.addEventListener('click', () => {
    const path = document.getElementById('tag-path').value.trim();
    const value = document.getElementById('tag-value').value;
    const title = `cmd:tag-write path=${path} value=${value}`;
    window.open(issueUrl(title, document.getElementById('tag-desc').value), '_blank');
    log('opened tag-write issue form', 'info');
  });
}
