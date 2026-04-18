# 🖍 ACG Whiteboard · P2P meeting board

Standalone P2P collaborative whiteboard. Open the page in two or more browsers
(or invite peers to the same room), and every stroke/clear is broadcast over
WebRTC data channels — no server, no account.

## Usage

- Navigate to `/guild/apps/whiteboard/` (or `/guild/apps/whiteboard/#room=sprint-review`)
- Pick a room name in the header and click **Join** (default: `acg-whiteboard`)
- Draw — strokes appear on every peer's canvas
- **pen** / **erase** / **size** / **color** controls in the toolbar
- **clear** wipes every peer's canvas

## How it works

1. Imports the mesh's `join` + `bcast` from `Enterprise/L2/scada/gateway/scripts/p2p.js`
2. Uses the tracker-based peer discovery already wired into the p2p app
3. Strokes travel as JSON `{t:'wb',kind:'stroke',stroke:{...}}` over the WebRTC
   data channels `acg`
4. Remote strokes arrive via `registerPeerHandler('wb', fn)` — a plugin hook
   added to `peers.js` so future apps can subscribe to their own `t:` type
5. Falls back to BroadcastChannel for same-browser tab sync (via the mesh
   infrastructure's native behavior)

## Dependencies

- `../../Enterprise/L2/scada/gateway/scripts/p2p.js`       (tracker + WebRTC)
- `../../Enterprise/L2/scada/gateway/scripts/peers.js`     (plugin hook)
- `../../Enterprise/L2/scada/gateway/scripts/auth.js`      (peer identity)
- `../../Enterprise/L2/scada/gateway/scripts/ui.js`        (log utility)
- `../../Enterprise/L2/scada/gateway/scripts/config.js`    (myId/myNm/myEm)
- `../../Enterprise/L2/scada/gateway/styles/theme.css` + `section.css`
