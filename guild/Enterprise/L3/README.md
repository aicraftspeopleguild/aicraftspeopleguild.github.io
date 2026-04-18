# Level 3 — Manufacturing Operations (MES)

> Scheduling, dispatching, editorial workflow, documentation, QA.
> See [ISA-95 L3 spec](../../../docs/engineering/architecture/isa-95/level-3-mes.md).

## What lives here

| Asset                      | Current path                                          |
|----------------------------|-------------------------------------------------------|
| Build orchestrator         | `scripts/build.sh` (11 steps)                         |
| View renderer              | `scripts/build.js`                                    |
| Perspective builder        | `scripts/perspective-build.js`                        |
| Entity ingest scripts      | `scripts/{white-papers,members,components,pages,apps}/` |
| Paper ingest (legacy)      | `guild/Enterprise/L4/api/white-papers/ingest.py`      |
| QA harnesses               | `scripts/test-{links,nav,browser}.{py,js}`            |
| Engineering docs           | `docs/engineering/**`                                 |
| UI component source        | `components/udts/` (design artefacts)                 |
| View templates             | `views/`, `perspective/views/`                        |
| Path UDT instances         | `components/udts/instances/paths/*.json`              |

## Workflows

- **W1 — Paper submission** — PR / Google Form / HTML form → auto-index → review → merge
- **W2 — Ritual experiment** — proposal → publish → post-period writeup
- **W3 — Member onboarding** — manifesto sign → profile PR → roster update

Each is driven by `.github/workflows/paper-index.yml` (L1 event) →
`scripts/build.sh` (L3 dispatcher) → PackML processes (L2) → `/api/*.json`
(L4 publication).
