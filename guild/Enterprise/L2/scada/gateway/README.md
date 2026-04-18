# controls/scada/gateway

🛰  **SCADA gateway** — host runtime that loads modules.  Each module owns
a tag namespace and follows the standard ACG provider contract
(`provider.py` + `udts.json` + `tags.json` + `index.html`).

This mirrors the Ignition Gateway pattern: a single host process exposes a
unified tag plant, and modules plug in to populate / consume slices of it.

```
controls/scada/gateway/
  styles/              🎨  HMI stylesheet bundle (theme + section + style)
  scripts/             🛰  ES-module runtime (every js/* module the HMIs need)
  providers/           📋  tag-provider registry (registry.json)
  auth/                🔑  identity module — owns auth.*
    provider.py            top-level (publishes auth.profile + auth.signedIn)
    udts.json   tags.json
    index.html             rendered via /index/renderer.js
    webrtc/               📡  cryptographic peer-id identity (passive)
    webtorrent/           🌊  tracker-based peer discovery (info_hash bearer)
    discord/              🎮  implicit-grant OAuth
    github/               🐙  device-flow OAuth (proxy required)
    google/               🔎  OIDC implicit (stub)
```

## What the gateway hosts

Every HMI in the project pulls **scripts**, **styles**, and **tag-provider
metadata** from this single location, giving the project page-to-page
consistency on theme, runtime, and namespace ownership.

## Sibling area

The SCADA gateway also hosts:

- `controls/scada/errors/`  ⚠ — gateway log ring buffer (errors.*)

`errors/` is *adjacent* (a peer of `gateway/`) rather than nested, so the
gateway-log viewer lives next to it at `/controls/scada/gateway/gateway-log.html`.

## Future modules under `gateway/`

- `gateway/devices/`       device-driver registry (Modbus, OPC-UA, …)
- `gateway/tags/`          centralised tag CRUD + RBAC
- `gateway/audit/`         signed audit trail of every tag write
- `gateway/scheduler/`     cron-style script execution

Every module follows the same provider contract — drop one in, register it
in `/controls/scada/gateway/providers/registry.json`, and the renderer
picks it up automatically.
