# Konomi Standard — Adopted in ACG

Imported from [ACGP2P](https://github.com/teslasolar/ACGP2P). Konomi is a
self-defining industrial-standards compression language with the motto
*"max info, min tokens"* — aligning perfectly with our 250-token-per-file rule.

## Layer model

| Layer | Purpose                                                     |
|-------|-------------------------------------------------------------|
| 0     | **meta** — STD, UDT, LEVEL, SM, ENTITY, RELATION, RULE, CROSSWALK |
| 1     | **base** — Identifier, Timestamp, Quality, Value, Range, Quantity, Duration, Status |
| 2     | ISA-95 (enterprise-control integration)                     |
| 3     | ISA-88 (batch control)                                      |
| 4     | ISA-101 (HMI design)                                        |
| 5     | ISA-18  (alarm management)                                  |
| 6     | OPC-UA                                                      |
| 7     | MQTT                                                        |
| 8     | Modbus                                                      |
| 9     | KPI (domain scorecards; the Guild also lives here)          |
| x     | **crosswalks** — mappings between any two layers            |

## Why we adopted it

The ACG was already using Ignition-style `Tag` UDTs (`path, value, quality, ts`). Konomi base layer defines `Value`, `Quality`, `Timestamp` with
full OPC-UA-compatible field lists. By adopting Konomi primitives we:

- Get OPC-UA quality codes (`GOOD=192`, `BAD=0`, `UNCERTAIN=64`, +flags)
- Gain `Quantity` (value + unit + uncertainty) for metric tags
- Pick up `Range` and `Duration` with industrial semantics
- Keep our existing `Tag`/`Paper`/`Member` UDTs at layer 9 (domain)

## Agents

Konomi defines 5 agent verbs for machine interaction:

| Agent      | Transform                   |
|------------|-----------------------------|
| parse      | doc → UDT                   |
| expand     | UDT → impl                  |
| validate   | impl → compliant            |
| crosswalk  | std_A ↔ std_B               |
| generate   | template → code             |

## Files in this import

- [base/](base/) — layer 1 primitive UDTs (imported verbatim)
- [meta/std.md](meta/std.md) — the Konomi root manifest
