# `controls/docs/standards/`

Industrial standards expressed as small (**≤250 token**) UDT JSON files,
following the **Konomi** self-defining standards compression meta-schema.

## Standards

| Dir | ID | Scope |
|-----|----|-------|
| `konomi/` | **Konomi v1.0** | Self-defining industrial standards compression (the meta-standard) |
| `gitplc/` | **GitPLC v1.0** | Universal PLC namespace UDT transfer layer (depends on Konomi) |

## Konomi layout

```
konomi/
├── _std.json                   standard header
├── meta/                       Layer 0 — how standards are defined
│   STD, UDT, LEVEL, STATE_MACHINE, ENTITY, RELATION, RULE, CROSSWALK
├── base/                       Layer 1 — primitives every standard uses
│   Identifier, Timestamp, Quality, Value, Range, Quantity, Duration, Status
├── isa95/                      Layer 2 — enterprise↔control integration
├── isa88/                      Layer 3 — batch control + state machines
├── isa101/                     Layer 4 — HMI design
├── isa18/                      Layer 5 — alarm management
├── opcua/                      Layer 6 — communication / address space
├── mqtt/                       Layer 7 — MQTT + Sparkplug B
├── modbus/                     Layer 8 — field protocol
├── kpi/                        Layer 9 — OEE/MTBF/MTTR/Downtime/FPY/...
└── crosswalks/                 standard ↔ standard mappings
```

## GitPLC layout

```
gitplc/
├── _std.json                   standard header
├── Agents.udt.json             α..κ pipeline roles
├── Layers.udt.json             layer summary (0..7)
├── Converters.udt.json         AB/Siemens/Codesys/Beckhoff/Omron/Mitsubishi
├── CLI.udt.json                gitplc command surface
├── RepoStructure.udt.json      on-disk project layout
├── Workflows.udt.json          import/export/CI flows
└── _index.json                 → template_root: ../../plc/git/
```

The concrete UDT instance templates (CM_Motor, CM_Valve, Equipment, etc.) live
at `controls/plc/git/` and are not duplicated here.

## File kinds

- `_std.json` — standard header (id, scope, version)
- `*.udt.json` — user-defined type
- `*.sm.json` — state machine
- `*.cw.json` — crosswalk (cross-standard mapping)
- `_index.json` — directory index

## Token budget

Every file is kept **under 250 tokens** so any single definition can be fed
whole into an LLM agent without truncation. Compact dot-path field names
(`timeouts.starting`) preserve structure while minimizing tokens.
