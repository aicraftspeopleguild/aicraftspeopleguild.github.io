# /guild/Enterprise

ISA-95 Enterprise layer — control-plane assets shared across Guild apps.

Moved here from `guild/apps/p2p/controls/` in April 2026 so that multiple
Guild apps (p2p mesh, future PLC dashboards, etc.) can share the same
SCADA gateway, tag database, HMI palette, and PLC templates without
having to fork the controls tree.

## Layout

```
guild/Enterprise/
├── README.md          ← this file (ISA-95 level index)
└── controls/
    ├── index.html     🎛 controls landing (NESW dock)
    ├── README.md      upstream-authored controls README
    ├── scada/         🖥  L2 — tag plant · HMI monitor · gateway
    │   ├── gateway/   🛰  host for namespace modules (auth.*, sub-providers)
    │   └── errors/    ⚠  gateway-log ring buffer · owns errors.*
    ├── hmi/           🖼  L2 — ISA-101 operator interface · palette · faceplates
    │   └── chat/      💬  P2P chat screen · owns chat.* room.* tracker.* signal.*
    ├── plc/           🔧  L1 — GitPLC universal PLC namespace + UDT templates
    ├── db/            🗄️  L2/L3 — canonical tag snapshot (tags.json)
    ├── sandbox/       🧪  L4 — browser-only tool workshops · owns sandbox.*
    └── docs/
        └── standards/ 📐  Konomi meta-standard + GitPLC standard
```

## ISA-95 level mapping

The ISA-95 control hierarchy classifies control-plane assets into five
levels (L0 physical through L4 enterprise). The existing `controls/`
folders map onto those levels as follows:

| Level | Role                          | Folders in `controls/`                                      |
|-------|-------------------------------|-------------------------------------------------------------|
| **L0** | Physical process              | *(none — mesh is fully virtual; no physical sensors)*       |
| **L1** | Sensing & manipulation / PLC  | [controls/plc/](controls/plc/)                              |
| **L2** | Monitoring & supervisory      | [controls/scada/](controls/scada/), [controls/hmi/](controls/hmi/) |
| **L3** | Manufacturing ops / historian | [controls/db/](controls/db/), [controls/scada/errors/](controls/scada/errors/) |
| **L4** | Business / enterprise         | [controls/sandbox/](controls/sandbox/)                      |

The folder structure was preserved on the move so that the hundreds of
intra-controls relative paths (`../scada/gateway/styles/section.css`,
`../../sandbox/shared/mesh-bridge.js`, etc.) continue to resolve. The
ISA-95 organisation is recorded in this index rather than imposed on
disk.

## Consumers

| App                                  | Imports from Enterprise/controls                        |
|--------------------------------------|---------------------------------------------------------|
| [`guild/apps/p2p/`](../apps/p2p/)    | `../../Enterprise/controls/*` for styles, scripts, links |

If a new Guild app needs the same controls, link to
`guild/Enterprise/controls/…` from that app's pages and add an entry
above.

## Adding new enterprise assets

Plant new control subsystems as sibling directories under
`Enterprise/controls/` following the provider contract documented in
[controls/README.md](controls/README.md) (`provider.py` + `udts.json`
+ `tags.json` + `index.html`). Update the ISA-95 table above so the
level classification stays accurate.
