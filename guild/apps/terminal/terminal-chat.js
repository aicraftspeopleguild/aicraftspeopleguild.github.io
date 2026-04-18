// ═══ ACG terminal · p2p chat bridge ═══
// Layered on top of the existing terminal (index.html). Joins the mesh
// and registers new commands:
//   chat <msg>    broadcast to peers in the current room
//   peers         list connected peers
//   join <room>   switch room
// Also renders incoming t:'msg' and t:'hi' traffic as terminal lines,
// so the terminal is fully interoperable with the existing chat app.
import {myId,myNm,myEm} from '../../Enterprise/L2/scada/gateway/scripts/config.js';
import {join,bcast,wsReady,announce} from '../../Enterprise/L2/scada/gateway/scripts/p2p.js';
import {pm,registerPeerHandler} from '../../Enterprise/L2/scada/gateway/scripts/peers.js';
import {log} from '../../Enterprise/L2/scada/gateway/scripts/ui.js';
import {startAuth,getProfile} from '../../Enterprise/L2/scada/gateway/scripts/auth.js';
import {startErrorCapture} from '../../Enterprise/L2/scada/gateway/scripts/errors.js';

const T = window.ACG_TERMINAL;
if (!T) { console.error('terminal-chat: ACG_TERMINAL not found'); }

const params = new URLSearchParams(location.hash.slice(1));
const roomName = params.get('room') || 'acg-guild';

// ── new commands registered on the existing COMMANDS registry
T.COMMANDS['chat'] = async (args) => {
  const txt = (args._rest || []).join(' ').trim();
  if (!txt) { T.line('  <span class="line-err">✗ usage: chat &lt;message&gt;</span>'); T.blank(); return; }
  const p = getProfile(), me = { name: p?.username || myNm, em: myEm, avatar: p?.avatar || null };
  const n = bcast(JSON.stringify({ t:'msg', id: myId, nm: me.name, em: me.em, av: me.avatar, txt }));
  T.line(`  <span class="line-dim">[→ ${n} peer${n===1?'':'s'}]</span>  <span class="line-val">${T.esc(txt)}</span>`);
  T.blank();
};

T.COMMANDS['peers'] = async () => {
  T.blank();
  if (pm.size === 0) { T.line('  <span class="line-dim">no peers connected</span>'); T.blank(); return; }
  T.line(`  <span class="line-head">${pm.size} peer${pm.size===1?'':'s'} in room</span>`);
  T.blank();
  for (const [pid, info] of pm.entries()) {
    T.line(`  <span class="line-key">${T.esc(pid.slice(-8))}</span>  <span class="line-val">${T.esc(info.name || '')}</span>  <span class="line-dim">${T.esc(info.emoji || '⚒')}</span>`);
  }
  T.blank();
};

T.COMMANDS['join'] = async (args) => {
  const room = (args._rest && args._rest[0]) || args.room || 'acg-guild';
  location.hash = 'room=' + encodeURIComponent(room);
  T.line(`  <span class="line-dim">→ joining room </span><span class="line-key">${T.esc(room)}</span>`);
  T.blank();
  join(room);
};

// ── incoming chat + presence
registerPeerHandler('msg', (m, rid) => {
  const pid = m.id || rid;
  const info = pm.get(pid) || { name: m.nm || pid.slice(-8), emoji: m.em || '⚒' };
  T.line(`  <span class="line-ok">[${T.esc(info.name)}]</span>  <span class="line-val">${T.esc(m.txt || '')}</span>`);
});
registerPeerHandler('hi', (m, rid) => {
  const nm = m.nm || rid.slice(-8);
  T.line(`  <span class="line-dim">· peer connected: </span><span class="line-key">${T.esc(nm)}</span><span class="line-dim"> (${T.esc(rid.slice(-8))})</span>`);
});

// ── mesh boot
startErrorCapture();
startAuth();
log('⚒ ACG terminal (chat bridge)', 'hi');
setTimeout(() => join(roomName), 400);
setInterval(() => { if (wsReady()) announce(); }, 30000);

// ── first-run hint in the terminal
setTimeout(() => {
  T.blank();
  T.line(`  <span class="line-dim">p2p chat bridge active · peer </span><span class="line-key">${myId.slice(-8)}</span><span class="line-dim"> · room </span><span class="line-key">${roomName}</span>`);
  T.line(`  <span class="line-dim">try: </span><span class="line-key">chat hello</span><span class="line-dim"> · </span><span class="line-key">peers</span><span class="line-dim"> · </span><span class="line-key">join &lt;room&gt;</span><span class="line-dim"> · </span><span class="line-key">heartbeat</span><span class="line-dim"> · </span><span class="line-key">watch demo.heartbeat</span>`);
  T.blank();
}, 1500);


// ── GitHub-Issue-backed tag DB ─────────────────────────────────────────
// Browser-side read-only client for the same tag DB that gh_tag.py drives.
// Hits the unauthenticated GitHub API — good for 60 req/hr per IP.
const GH_REPO = 'teslasolar/aicraftspeopleguild.github.io';
const GH_API  = 'https://api.github.com';

function _parseFencedJSON(body) {
  if (!body) return {};
  let t = String(body).trim();
  if (t.startsWith('```')) {
    t = t.split('\n').slice(1).join('\n');
    if (t.endsWith('```')) t = t.slice(0, -3);
    if (t.trimStart().startsWith('json')) t = t.trimStart().slice(4).trimStart();
  }
  try { return JSON.parse(t); } catch { return { raw: body }; }
}

async function ghFindIssue(path) {
  // No search API (indexing lag) — walk label=tag issues by title.
  for (const state of ['open', 'closed']) {
    const r = await fetch(`${GH_API}/repos/${GH_REPO}/issues?labels=tag&state=${state}&per_page=100`, {
      headers: { Accept: 'application/vnd.github+json' }
    });
    if (!r.ok) throw new Error(`github ${r.status}`);
    const list = await r.json();
    const hit = list.find(i => i.title === `tag:${path}`);
    if (hit) return hit;
  }
  return null;
}

async function ghReadTag(path) {
  const iss = await ghFindIssue(path);
  if (!iss) return { ok: false, error: `no tag '${path}' on ${GH_REPO}` };
  let body = iss.body;
  if (iss.comments > 0) {
    const cr = await fetch(iss.comments_url + '?per_page=100', {
      headers: { Accept: 'application/vnd.github+json' }
    });
    if (cr.ok) {
      const cs = await cr.json();
      if (cs.length) body = cs[cs.length - 1].body;
    }
  }
  const v = _parseFencedJSON(body);
  return {
    ok: true, path, issue: iss.number, url: iss.html_url,
    value: v.value, quality: v.quality || 'good', type: v.type,
    description: v.description, updated_at: v.updated_at || iss.updated_at,
  };
}

T.COMMANDS['gh-tag:read'] = async (args) => {
  const path = args.path || (args._rest && args._rest[0]);
  if (!path) { T.line('  <span class="line-err">✗ usage: gh-tag:read path=demo.heartbeat</span>'); T.blank(); return; }
  try {
    const r = await ghReadTag(path);
    if (!r.ok) { T.line(`  <span class="line-err">✗ ${T.esc(r.error)}</span>`); T.blank(); return; }
    T.blank();
    T.kv('path      ', r.path);
    T.kv('value     ', r.value == null ? '—' : JSON.stringify(r.value), 'line-ok');
    T.kv('quality   ', r.quality, 'line-dim');
    T.kv('type      ', r.type || '—', 'line-dim');
    T.kv('updated_at', r.updated_at, 'line-dim');
    T.kv('issue     ', `#${r.issue} · ${r.url}`, 'line-dim');
    T.blank();
  } catch (e) { T.line(`  <span class="line-err">✗ ${T.esc(e.message)}</span>`); T.blank(); }
};

T.COMMANDS['heartbeat'] = async () => {
  try {
    const r = await ghReadTag('demo.heartbeat');
    if (!r.ok) { T.line(`  <span class="line-err">✗ ${T.esc(r.error)}</span>`); T.blank(); return; }
    const cmd = await ghReadTag('demo.terminal-cmd');
    T.blank();
    T.line(`  <span class="line-ok">💓</span> <span class="line-key">demo.heartbeat</span>  <span class="line-val">${T.esc(String(r.value))}</span>  <span class="line-dim">· updated ${T.esc(r.updated_at||'—')}</span>`);
    if (cmd.ok) T.line(`  <span class="line-dim">↳ last command: </span><span class="line-val">${T.esc(String(cmd.value))}</span>`);
    T.blank();
  } catch (e) { T.line(`  <span class="line-err">✗ ${T.esc(e.message)}</span>`); T.blank(); }
};

// watch <path> — poll every 15s and print when the value changes. `watch` alone
// (no arg) watches demo.heartbeat. `watch off` stops all watchers.
const _watchers = new Map();
T.COMMANDS['watch'] = async (args) => {
  const arg0 = (args._rest && args._rest[0]) || 'demo.heartbeat';
  if (arg0 === 'off') {
    for (const [, id] of _watchers) clearInterval(id);
    _watchers.clear();
    T.line('  <span class="line-dim">· all watchers stopped</span>'); T.blank(); return;
  }
  if (_watchers.has(arg0)) {
    T.line(`  <span class="line-dim">already watching </span><span class="line-key">${T.esc(arg0)}</span>`); T.blank(); return;
  }
  let last = null;
  const tick = async () => {
    try {
      const r = await ghReadTag(arg0);
      if (!r.ok) return;
      const v = JSON.stringify(r.value);
      if (v !== last) {
        T.line(`  <span class="line-purple">◉ watch </span><span class="line-key">${T.esc(arg0)}</span><span class="line-dim"> → </span><span class="line-val">${T.esc(v)}</span><span class="line-dim"> @ ${T.esc(r.updated_at||'')}</span>`);
        last = v;
      }
    } catch {}
  };
  await tick();
  _watchers.set(arg0, setInterval(tick, 15000));
  T.line(`  <span class="line-ok">◉ watching </span><span class="line-key">${T.esc(arg0)}</span><span class="line-dim"> (15s poll · </span><span class="line-key">watch off</span><span class="line-dim"> to stop)</span>`);
  T.blank();
};
