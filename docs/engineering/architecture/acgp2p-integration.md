---
acg-paper:
  id: ACG-ARCH-ACGP2P-2026
  type: standard
  title: "ACGP2P Integration Notes"
  author: "AI Craftspeople Guild"
  date: 2026-04-18
  status: published
  tags: [acgp2p, konomi, isa-95, scada, hmi, architecture]
  abstract: >
    What we borrowed from the sibling ACGP2P repo and how it strengthens
    the main Guild site architecture.
---

# ACGP2P Integration Notes

ACGP2P (`github.com/teslasolar/ACGP2P`) is a peer-to-peer, serverless,
SCADA-instrumented chat mesh. Its `controls/` tree implements a complete
ISA-95-styled architecture with the **Konomi** standard as the UDT
description language. Several of its patterns map directly onto our
site's needs.

## What we borrowed

### 1. Konomi base primitives

`docs/templates/konomi/base/` — imported verbatim (compact `konomi/udt/v1`
schema):

- **Value** (v, q, t, unit) — the universal tag container
- **Quality** — OPC-UA style codes (GOOD=192, BAD=0, UNCERTAIN=64 + flags)
- **Timestamp** — ISO8601 / EPOCH_MS / OPC_FILETIME encodings
- **Identifier** (UUID, PATH, TAG, URN) — identifier families
- **Quantity** — value + unit + uncertainty
- **Range** / **Duration** / **Status**

These upgrade our existing `Tag` UDT from `(path, value, quality, ts)` to a
fully industrial-grade type backbone.

### 2. Layered standards model

Konomi's layer stack maps neatly onto our ISA-95 docs:

| Konomi layer    | ACG equivalent                                    |
|-----------------|---------------------------------------------------|
| 0 meta          | `docs/engineering/tech-spec/udt-system.md`        |
| 1 base          | `docs/templates/konomi/base/` (new)               |
| 2 ISA-95        | `docs/engineering/architecture/isa-95/`           |
| 3-5 ISA-88/101/18 | Future work                                     |
| 9 KPI / domain  | Our Paper / Member / Program / App UDTs          |

### 3. Runtime tags.json

ACGP2P's `controls/db/tags.json` is a live JSON tag database that dashboards
read directly (via shields.io dynamic badges). We ported the shape and
generate our own from the SQLite catalog every build:

`guild/Enterprise/L4/runtime/tags.json` carries `sys`, `enterprise`, `catalog`,
`pipeline`, `identity` tag groups — each field a Konomi Value record.
Consumed by the site's dashboards and by external clients via the API v1.0
surface.

### 4. HMI template layers (future)

ACGP2P separates HMI into `badges/` + `faceplate/` + `layers/`. We have the
equivalent split as: small `acg.display.badge` / composite `acg.card.*` /
dock `acg.dock.*` components. Future: formalize a `faceplate` component
type mirroring ACGP2P's pattern for member + paper detail views.

### 5. SCADA gateway (future)

ACGP2P has `controls/scada/gateway/` with per-provider auth (discord,
github, google, webrtc, webtorrent). When we add MCP-over-SSE and GitHub
OAuth for the Guild, this pattern is the model.

## What we did *not* borrow

- Peer-to-peer messaging / WebRTC signalling (irrelevant for a doc site)
- Tracker announce / offers-in / answers-out (P2P-specific)
- WebTorrent integration (chat-mesh specific)

## File index

- `docs/templates/konomi/README.md`
- `docs/templates/konomi/base/*.udt.json` — 8 primitives
- `docs/templates/konomi/meta/_std.json` — Konomi layer manifest
- `guild/Enterprise/L4/runtime/tags.json` — live enterprise tag snapshot
- `guild/web/scripts/api/build-runtime-tags.py` — generator
