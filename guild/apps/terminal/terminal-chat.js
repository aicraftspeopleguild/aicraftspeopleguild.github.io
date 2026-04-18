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
  T.line(`  <span class="line-dim">try: </span><span class="line-key">chat hello</span><span class="line-dim"> · </span><span class="line-key">peers</span><span class="line-dim"> · </span><span class="line-key">join &lt;room&gt;</span>`);
  T.blank();
}, 1500);
