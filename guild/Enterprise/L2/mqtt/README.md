# ACG MQTT · topic pub/sub over the WebRTC mesh

Single-file, zero-dep pub/sub for the browser, with MQTT-shaped
semantics (topics, wildcards, retained) on top of the existing ACG
mesh. One shared vocabulary across tags, script events, and peer
traffic — a topic path is a tag path is a script trigger.

## API

```js
import mqtt, { subscribe, publish, matchTopic, peek, attachMesh }
  from './mqtt.js';

// local-only pub/sub
const unsub = subscribe('peer.*.state', (topic, msg, rec) => {
  console.log(topic, msg, rec.from, rec.retained);
});
publish('peer.abc.state', 'connected');

// retained: new subscribers of the same topic get this immediately
publish('room.name', 'acg-whiteboard', { retained: true });

// mesh attach: publishes also reach other peers in the current room
import * as p2p from '../scada/gateway/scripts/p2p.js';
import * as peers from '../scada/gateway/scripts/peers.js';
import { myId } from '../scada/gateway/scripts/config.js';
attachMesh({ bcast: p2p.bcast, registerPeerHandler: peers.registerPeerHandler, myId });
```

## Wildcards

| pattern      | matches                         | not                       |
|--------------|---------------------------------|---------------------------|
| `peer.*.state`      | `peer.abc.state`         | `peer.state`, `peer.a.b.state` |
| `peer.#`            | `peer.abc`, `peer.abc.state`, `peer.abc.dc.open` | `peer` |
| `#`                 | anything                 | (nothing)                 |

`*` matches exactly one segment, `#` matches the rest of the path.

## Retained messages

`publish(topic, msg, { retained: true })` stores the message. Any new
`subscribe(topic)` whose pattern matches gets the retained value
replayed immediately — same as MQTT retained topics.

`peek(topic)` returns the last retained record or `null`. Useful for
"what's the current value" without subscribing.

## Mesh transport

When `attachMesh` is called, every non-local publish also fans out
over the WebRTC data channel `bcast` as `{t:'mqtt', rec}`. Remote
peers with the mesh handler wired call back into `publish(…,
{_fromPeer:true})` so their local subscribers fire. No loopback — a
peer that receives an MQTT envelope does not re-broadcast.

## Topic catalogue

See `docs/engineering/connection-events.md` for the current vocabulary
(tracker.*, signal.*, peer.*, room.*, api.*, packml.*, pipeline.*).
Every `@tag-event` header in the repo is effectively a subscription on
one of those topics.

## Live demo

Open `guild/Enterprise/L2/mqtt/` in a browser. The page:
- auto-attaches to the mesh and joins room `mqtt-bus`
- defaults to subscribing `#` (everything)
- lets you add more patterns, publish, toggle retained
- runs 5 self-tests on load (visible in the footer strip)

Open two tabs in the same room to watch cross-peer publishes land.

## Python counterpart · `bin/acg-mqtt.py`

Headless subscriber that polls the GitHub-Issues tag DB and fires a
callback on change. Not a real MQTT broker — it's the durable-tag
side of the pair. The browser is the live side.

## Relationship to existing concepts

- **tag path == topic**
- **script `@tag-event` == subscription**
- **retained == GH-Issues backed tag value**
- **publish with `local:true` == local bus only, no peer fanout**

An MQTT-subscriber script could live in `L3/udts/script/` with a
trigger like `{kind:"on_publish", topic:"peer.*.state"}` once the
matcher learns `*` wildcards — that upgrade is queued for the next PR.
