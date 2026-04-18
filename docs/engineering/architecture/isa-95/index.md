---
acg-paper:
  id: ACG-ARCH-ISA95-2026
  type: standard
  title: "Guild as ISA-95 Enterprise"
  author: "AI Craftspeople Guild"
  date: 2026-04-18
  status: published
  tags: [isa-95, architecture, erp, mes, scada, governance]
  abstract: >
    Model the AI Craftspeople Guild as a 5-level ISA-95 enterprise. Maps
    every existing Guild asset (papers, members, rituals, PackML programs,
    SQLite DB, API) to the appropriate level: L0 physical (authored work),
    L1 sensing (git events, form submits), L2 SCADA (PackML supervision),
    L3 MES (scheduling + documentation), L4 ERP (manifesto, membership,
    catalog). Clarifies where each kind of data lives and why.
---

# Guild as ISA-95 Enterprise

*ACG-ARCH-ISA95-2026 · AI Craftspeople Guild*

The ISA-95 standard (Enterprise-Control System Integration) defines 5 levels from physical production up to business planning. Mapping the Guild onto these levels gives a coherent picture of which data belongs where, what flows up, and what flows down.

```
┌──────────────────────────────────────────────────────────────┐
│ Level 4 — Enterprise (ERP)                                   │
│ Manifesto, membership, paper catalog, governance, API        │
│ Time horizon: months / years                                 │
├──────────────────────────────────────────────────────────────┤
│ Level 3 — Manufacturing Operations (MES)                     │
│ Build pipeline scheduling, documentation, editorial workflow │
│ Time horizon: hours / days                                   │
├──────────────────────────────────────────────────────────────┤
│ Level 2 — Supervisory / SCADA                                │
│ PackML state machines, run monitoring, health dashboards     │
│ Time horizon: seconds / minutes                              │
├──────────────────────────────────────────────────────────────┤
│ Level 1 — Sensing / Control                                  │
│ git hooks, PR events, form submissions, ingest triggers      │
│ Time horizon: milliseconds                                   │
├──────────────────────────────────────────────────────────────┤
│ Level 0 — Physical Process                                   │
│ Actual authoring, thinking, mob sessions, code being written │
│ Time horizon: real human work                                │
└──────────────────────────────────────────────────────────────┘
```

## Per-level spec

- [Level 0 — Physical Process](level-0-physical.md)
- [Level 1 — Sensing & Control](level-1-sensing.md)
- [Level 2 — Supervisory / SCADA](level-2-scada.md)
- [Level 3 — Manufacturing Operations (MES)](level-3-mes.md)
- [Level 4 — Enterprise (ERP)](level-4-erp.md)

## Cross-level flows

| From | To   | Example                                                       |
|------|------|---------------------------------------------------------------|
| L0   | L1   | Author writes a paper → git commit event                      |
| L1   | L2   | PR merge triggers `paper-index.yml` workflow                  |
| L2   | L3   | PackML COMPLETE state → release dispatches downstream build   |
| L3   | L4   | Build pipeline writes `papers.json` → ERP catalog updated     |
| L4   | L3   | New paper type added to enum → MES workflow template updated  |
| L4   | L2   | Manifesto signed → SCADA records new signatory event          |
