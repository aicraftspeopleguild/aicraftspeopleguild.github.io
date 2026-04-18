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
├── L0/                    physical process
│   └── README.md          human work: authoring, mobbing (no sensors)
│
├── L1/                    sensing & manipulation · PLC
│   ├── forms/             📝 article-submission forms (event router)
│   ├── plc/               🔧 GitPLC universal PLC namespace + UDT templates
│   └── README.md
│
├── L2/                    monitoring & supervisory
│   ├── lib/               🐍 PackML engine library (packml.py, git_ops.py, …)
│   ├── scada/             🖥  tag plant · gateway host · errors ring buffer
│   │   ├── gateway/       🛰  host for namespace modules (auth.*, sub-providers)
│   │   └── errors/        ⚠  gateway-log ring buffer · owns errors.*
│   ├── hmi/               🖼  ISA-101 operator interface · palette · faceplates
│   │   └── chat/          💬 P2P chat screen · owns chat.* room.* tracker.* signal.*
│   ├── state/             📊 PackML state-machine snapshots (*.state.json)
│   ├── tag.db             🗄️ local-tier tag database
│   └── README.md
│
├── L3/                    manufacturing operations · MES · historian
│   ├── automation/        ⚙️  Script UDT instances (event-driven build triggers)
│   ├── components/        🧩 UI component design artefacts (UDT instances + templates)
│   ├── db/                🗄️ p2p canonical tag snapshot (tags.json, tags.sqlite)
│   ├── perspective/       👁  Perspective view templates
│   ├── scripts/           🔧 build pipeline · ingest · QA harnesses
│   ├── tools/             🛠  Tool UDT instances (build, test, git, state-machine)
│   ├── views/             📄 view templates (*.view.json)
│   └── README.md          build pipeline doc
│
├── L4/                    business / enterprise · ERP
│   ├── api/               📡 static JSON API (papers/members/health) + build scripts
│   ├── csv/               📑 dense CSV catalogs
│   ├── database/          🗄️ SQLite ERP store (acg.db + init-db.py)
│   ├── members/           👥 member master data (originals + UDT instances)
│   ├── programs/          📋 program UDT master data (templates + instances)
│   ├── runtime/           ⚡ live enterprise tag snapshot (tags.json)
│   ├── sandbox/           🧪 browser-only tool workshops · owns sandbox.*
│   └── README.md
│
└── docs/
    └── standards/         📐 Konomi meta-standard + GitPLC standard
```

## ISA-95 level mapping

| Level | Role                          | Contents                                                    |
|-------|-------------------------------|-------------------------------------------------------------|
| **L0** | Physical process              | [L0/](L0/) — human authoring/mobbing (mesh is fully virtual) |
| **L1** | Sensing & manipulation / PLC  | [L1/plc/](L1/plc/), [L1/forms/](L1/forms/)                  |
| **L2** | Monitoring & supervisory      | [L2/lib/](L2/lib/), [L2/scada/](L2/scada/), [L2/hmi/](L2/hmi/), [L2/state/](L2/state/) |
| **L3** | Manufacturing ops / historian | [L3/scripts/](L3/scripts/), [L3/views/](L3/views/), [L3/components/](L3/components/), [L3/perspective/](L3/perspective/), [L3/tools/](L3/tools/), [L3/automation/](L3/automation/), [L3/db/](L3/db/) |
| **L4** | Business / enterprise · ERP   | [L4/api/](L4/api/), [L4/members/](L4/members/), [L4/programs/](L4/programs/), [L4/csv/](L4/csv/), [L4/database/](L4/database/), [L4/runtime/](L4/runtime/), [L4/sandbox/](L4/sandbox/) |

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

