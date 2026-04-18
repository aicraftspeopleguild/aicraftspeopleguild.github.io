# Level 2 — Supervisory / SCADA

> PackML state machines, run monitoring. Every pipeline step supervised.
> See [ACG-STD-PACKML-2026](../../../docs/engineering/standards/packml.md).

## What lives here

| Asset                      | Current path                                          |
|----------------------------|-------------------------------------------------------|
| PackML library             | `lib/` — state machine engine                         |
| State logs                 | `state/*.state.json` — latest run per program         |
| Run history (DB mirror)    | L4 `packml_runs` table                                |
| Program UDT instances      | `guild/Enterprise/L4/programs/instances/*.json`       |

## Invariants

- Every program starts at `IDLE` on each run (no sticky state).
- State writes are atomic.
- Pre-check failure → `HELD` (no execute, pipeline skips cleanly).
- Exception → `ABORTED` with captured traceback.
- Post-check failure → `ABORTED` with reason.
