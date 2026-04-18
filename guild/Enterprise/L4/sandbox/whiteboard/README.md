# controls/sandbox/whiteboard

🖍  **Shared whiteboard** — canvas relayed over the ACG peer mesh via
the sandbox `BroadcastChannel('acg-mesh')` bridge.

## What it does

- Canvas fills the viewport (high-DPI aware).
- Pen + eraser tools, colour picker, stroke width 1-20 px.
- Each finished stroke is published via the mesh bridge as a
  `whiteboard / stroke` envelope.
- Subscribes to every `whiteboard / *` envelope and replays remote
  strokes and `clear` events locally.
- Presence pings every 5 s; peer count shown in the toolbar.

## Envelope shapes

```jsonc
// stroke finished
{ "source":"whiteboard", "type":"stroke", "path":"stroke",
  "value":{ "id":"wb-abcdefgh", "tool":"pen|erase", "color":"#1a5c4c",
             "size":3, "pts":[[x,y],…], "ts":1700… }, "ts":1700… }

// clear button
{ "source":"whiteboard", "type":"clear", "path":"clear",
  "value":{ "by":"wb-abcdefgh" }, "ts":1700… }

// presence
{ "source":"whiteboard", "type":"ping|join|leave",
  "value":{ "id":"wb-abcdefgh" }, "ts":1700… }
```

`pts` are **normalised coordinates** in `[0,1]²` so different canvas
sizes on different tabs render the same drawing.

## Tags (via sandbox-bridge)

When the main chat tab is open, the host-side bridge at
`controls/scada/gateway/scripts/sandbox-bridge.js` relays every envelope
into the tag plant:

```
sandbox.whiteboard.lastEventAt       ms
sandbox.whiteboard.lastEvent         UDT:Envelope
sandbox.whiteboard.events.stroke.count   UDT:Counter
sandbox.whiteboard.events.clear.count
sandbox.whiteboard.events.ping.count
```

## Scope

MVP is cross-tab (same browser) via `BroadcastChannel`.  Cross-peer
sync over WebRTC is out of scope for the MVP — that would need the
chat page to relay `whiteboard/*` envelopes out via `bcast()` and
route incoming peer messages back into the sandbox channel.
