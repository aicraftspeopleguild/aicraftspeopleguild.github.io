# controls/scada/gateway/scripts

🛰  **Gateway-managed runtime** — every browser ES module loaded by an
HMI page lives here.  The SCADA gateway is the single home for the
JavaScript runtime so HMIs can pull script + tag + style off one host.

```
scripts/
  main.js            entry point — wires handlers, seeds sys.*, starts services
  ui.js              $/log/badge primitives reused everywhere
  config.js          OAUTH/ICE/TRACKERS + peer id minting
  p2p.js             RTCPeerConnection + WebTorrent tracker dance
  peers.js           pm map · per-peer state · channel wiring
  chat.js            send / receive · chat ring
  auth.js            OAuth flows (discord/github), profile broker
  version.js         GitHub-API commit-pill poll
  errors.js          ring-buffer logger (writes errors.*)
  sandbox-bridge.js  BroadcastChannel host-side bridge
  scada/
    tags.js          tag plant (path-addressed, quality-tagged, pub/sub)
    providers.js     namespace owner enum (mirrors providers/registry.json)
    monitor.js       SCADA drawer + faceplate render (Ctrl+. toggle)
    udt.js           UDT validator + builder
    index.js         public re-exports
```

## Contract

- Every page that needs runtime imports `controls/scada/gateway/scripts/main.js`
  (or a specific submodule).
- Internal imports use `./` paths — moving the directory keeps every
  internal import valid.
- Manifests under `controls/scada/programs/acg/` reference the new
  `controls/scada/gateway/scripts/...` paths.

## Reference paths

| Loader page                  | Script src |
|------------------------------|------------|
| `/index.html`                | `controls/scada/gateway/scripts/main.js` |
| `/health.html`               | `./controls/scada/gateway/scripts/config.js` |
