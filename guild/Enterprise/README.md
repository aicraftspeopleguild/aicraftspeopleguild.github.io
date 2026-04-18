# /guild/Enterprise

ISA-95 Enterprise layer — control-plane assets shared across Guild apps.

Moved here from `guild/apps/p2p/controls/` in April 2026 so that multiple
Guild apps (p2p mesh, future PLC dashboards, etc.) can share the same
SCADA gateway, tag database, HMI palette, and PLC templates without
having to fork the controls tree. Subsequently reorganised into ISA-95
level directories.

## Layout

```
guild/Enterprise/
├── README.md              ← this file (ISA-95 level index)
├── index.html             🎛 controls landing (NESW dock)
├── controls-README.md     upstream-authored controls README (pre-split)
│
├── L1/                    sensing & manipulation · PLC
│   └── plc/               🔧 GitPLC universal PLC namespace + UDT templates
│
├── L2/                    monitoring & supervisory
│   ├── scada/             🖥  tag plant · gateway host · errors ring buffer
│   │   ├── gateway/       🛰  host for namespace modules (auth.*, sub-providers)
│   │   └── errors/        ⚠  gateway-log ring buffer · owns errors.*
│   └── hmi/               🖼  ISA-101 operator interface · palette · faceplates
│       └── chat/          💬 P2P chat screen · owns chat.* room.* tracker.* signal.*
│
├── L3/                    manufacturing operations · historian
│   └── db/                🗄️ canonical tag snapshot (tags.json)
│
├── L4/                    business / enterprise
│   └── sandbox/           🧪 browser-only tool workshops · owns sandbox.*
│
└── docs/
    └── standards/         📐 Konomi meta-standard + GitPLC standard
```

## ISA-95 level mapping

| Level | Role                          | Contents                                                    |
|-------|-------------------------------|-------------------------------------------------------------|
| **L0** | Physical process              | *(none — mesh is fully virtual; no physical sensors)*       |
| **L1** | Sensing & manipulation / PLC  | [L1/plc/](L1/plc/)                                          |
| **L2** | Monitoring & supervisory      | [L2/scada/](L2/scada/), [L2/hmi/](L2/hmi/)                  |
| **L3** | Manufacturing ops / historian | [L3/db/](L3/db/), [L2/scada/errors/](L2/scada/errors/) *(logically L3, lives under scada)* |
| **L4** | Business / enterprise         | [L4/sandbox/](L4/sandbox/)                                  |

`docs/` is not a control level — it holds the standards (Konomi, GitPLC)
that govern the levels above.

## Cross-level pathing

Subsystems at the same level keep sibling paths (`L2/hmi/` ↔ `L2/scada/`
use `../scada/…`). Cross-level references traverse via the level
folder, e.g. from `L3/db/index.html`:

```
../../L2/scada/gateway/styles/section.css
../../L4/sandbox/shared/mesh-bridge.js
```

See `guild/Enterprise/index.html` for the reference shell and
`../apps/p2p/index/renderer.js` for the `SUBSYSTEMS` path table.

## Consumers

| App                                  | Imports from Enterprise                                     |
|--------------------------------------|-------------------------------------------------------------|
| [`guild/apps/p2p/`](../apps/p2p/)    | `../../Enterprise/L{1,2,3,4}/*` for styles, scripts, links  |

If a new Guild app needs the same controls, link to
`guild/Enterprise/L{n}/{sub}/…` from that app's pages and add a row
here.

## Adding new enterprise assets

Plant new control subsystems as sibling directories under the matching
level folder, following the provider contract documented in
[controls-README.md](controls-README.md) (`provider.py` + `udts.json`
+ `tags.json` + `index.html`). Update the ISA-95 table above so the
level classification stays accurate, and register the new subsystem in
`../apps/p2p/index/renderer.js` (`SUBSYSTEMS` array) so it appears in
the sitemap.

