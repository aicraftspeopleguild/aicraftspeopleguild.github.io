# Level 3 — Manufacturing Operations (MES)

> Scheduling, dispatching, editorial workflow, documentation, QA.
> See [ISA-95 L3 spec](../../docs/engineering/architecture/isa-95/level-3-mes.md).

## What lives here

| Asset                      | Current path                                          |
|----------------------------|-------------------------------------------------------|
| Build orchestrator         | `guild/web/scripts/build.sh` (11 steps)               |
| View renderer              | `guild/web/scripts/build.js`                          |
| Perspective builder        | `guild/web/scripts/perspective-build.js`              |
| Entity ingest scripts      | `guild/web/scripts/{white-papers,members,components,pages,apps}/` |
| Paper ingest (legacy)      | `guild/web/white-papers/ingest.py`                    |
| QA harnesses               | `guild/web/scripts/test-{links,nav,browser}.{py,js}`  |
| Engineering docs           | `docs/engineering/**`                                 |
| UI component source        | `guild/web/components/udts/**` (design artefacts)     |
| View templates             | `guild/web/views/**`, `guild/web/perspective/views/` |
| Path UDT instances         | `guild/web/components/udts/instances/paths/*.json`    |

## Workflows

- **W1 — Paper submission** — PR / Google Form / HTML form → auto-index → review → merge
- **W2 — Ritual experiment** — proposal → publish → post-period writeup
- **W3 — Member onboarding** — manifesto sign → profile PR → roster update

Each is driven by `.github/workflows/paper-index.yml` (L1 event) →
`build.sh` (L3 dispatcher) → PackML processes (L2) → `/api/*.json`
(L4 publication).
