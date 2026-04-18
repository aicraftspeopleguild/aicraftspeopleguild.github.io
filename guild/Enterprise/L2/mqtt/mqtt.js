// ═══ ACG MQTT-shaped pub/sub ═════════════════════════════════════════
// Topic-based pub/sub that mirrors MQTT semantics but uses the existing
// ACG mesh as transport. Topics == tag paths ("peer.abc.state",
// "tracker.current.state", "room.peerCount"). One message type per
// publish: {topic, msg, retained?, ts, from}.
//
// Wildcards:
//   *   matches exactly one segment  (peer.*.state)
//   #   matches the rest of the path (peer.#  /  #)
//
// Transport:
//   Local subscribers always fire synchronously.
//   If p2p is available and `bcast()` is importable, publishes with
//   `local:false` (default) also propagate to every connected peer.
//   Peers with `registerPeerHandler('mqtt', ...)` wired call back into
//   here and fire local subscribers on their side.
//
// No external broker, no websocket server. A single file, zero deps.

const subs = [];           // [{pattern, re, fn, id}]
const retained = new Map();// topic -> last message {topic,msg,ts,retained:true}
let nextSubId = 1;

let bcastFn  = null;       // optional: p2p bcast(str)
let myId     = 'local';    // optional: local peer id
let peerRecv = null;       // optional: unregister fn

// ── topic pattern matching ───────────────────────────────────────────
function patternToRegex(pattern) {
  // Escape regex chars EXCEPT our wildcards, then substitute them.
  const esc = pattern.replace(/[.+?^${}()|[\]\\]/g, '\\$&');
  const re  = esc.replace(/\*/g, '[^.]+').replace(/#/g, '.*');
  return new RegExp('^' + re + '$');
}

export function matchTopic(pattern, topic) {
  return patternToRegex(pattern).test(topic);
}

// ── local api ────────────────────────────────────────────────────────
export function subscribe(pattern, fn, opts = {}) {
  const id = nextSubId++;
  const entry = { id, pattern, re: patternToRegex(pattern), fn };
  subs.push(entry);
  // Replay retained messages whose topic matches this new subscription.
  if (opts.replayRetained !== false) {
    for (const [topic, rec] of retained) {
      if (entry.re.test(topic)) {
        try { fn(topic, rec.msg, rec); } catch (e) { console.error('mqtt sub err', e); }
      }
    }
  }
  return () => unsubscribe(id);
}

export function unsubscribe(id) {
  const i = subs.findIndex(s => s.id === id);
  if (i >= 0) subs.splice(i, 1);
}

export function publish(topic, msg, opts = {}) {
  const rec = {
    topic,
    msg,
    ts:       Date.now(),
    from:     opts.from || myId,
    retained: !!opts.retained,
    qos:      opts.qos || 0,
  };
  // Retained = remember last value, new subscribers get it immediately
  if (rec.retained) retained.set(topic, rec);
  // Fire local subscribers
  for (const s of subs) {
    if (s.re.test(topic)) {
      try { s.fn(topic, msg, rec); } catch (e) { console.error('mqtt sub err', e); }
    }
  }
  // Fan out to peers unless caller said local-only or this came from a peer
  if (!opts.local && !opts._fromPeer && bcastFn) {
    try { bcastFn(JSON.stringify({ t: 'mqtt', rec })); } catch (e) { /* mesh not ready */ }
  }
  return rec;
}

// ── convenience ──────────────────────────────────────────────────────
export function peek(topic) {
  return retained.get(topic) || null;
}
export function clearRetained(topic) {
  if (topic) retained.delete(topic);
  else retained.clear();
}
export function listSubscriptions() {
  return subs.map(s => ({ id: s.id, pattern: s.pattern }));
}
export function stats() {
  return {
    subs:     subs.length,
    retained: retained.size,
    connectedToMesh: !!bcastFn,
    myId,
  };
}

// ── optional mesh integration ────────────────────────────────────────
// Call once from your app after importing peers.js / p2p.js.
export function attachMesh({ bcast, registerPeerHandler, myId: id } = {}) {
  if (bcast) bcastFn = bcast;
  if (id) myId = id;
  if (registerPeerHandler) {
    if (peerRecv) peerRecv();
    registerPeerHandler('mqtt', (m /*, rid */) => {
      if (!m || !m.rec) return;
      // Re-publish locally only; do NOT fan out again.
      publish(m.rec.topic, m.rec.msg, {
        ...m.rec,
        local:      true,
        _fromPeer:  true,
      });
    });
    peerRecv = () => {}; // placeholder — peers.js doesn't expose unregister
  }
}

// ── default export for convenience ───────────────────────────────────
export default { subscribe, unsubscribe, publish, peek, matchTopic,
  clearRetained, listSubscriptions, stats, attachMesh };
