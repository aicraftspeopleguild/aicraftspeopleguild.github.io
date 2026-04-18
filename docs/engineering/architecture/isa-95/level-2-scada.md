# Level 2 — Supervisory / SCADA

*State-machine supervision of every automated process. Real-time dashboards.*

## Core abstraction: PackML

Every build pipeline step is a `Process` running through the ISA-TR88.00.02 core state model: **IDLE → STARTING → EXECUTE → COMPLETING → COMPLETE**, or
**→ ABORTING → ABORTED** on failure; **HELD** when pre-checks fail before execute.

See [ACG-TS-PackML](../../../standards/packml.md) for the full spec. Implementation: `guild/web/scripts/lib/packml_process.py`.

## What L2 monitors

| Process                        | Pre-checks                      | Post-checks                      |
|--------------------------------|---------------------------------|----------------------------------|
| `components:catalog`           | instance dir exists, ≥10 files  | tags/index.json + index.json written |
| `apps:papers`                  | WP instances + template exist   | ≥10 App instances, data, pages   |
| `api:build`                    | DB file exists                  | papers/members/health.json exist |
| `ingest.py` (white papers)     | originals dir exists            | index.json written               |
| `init-db`                      | schema files exist              | acg.db created, rowcounts > 0    |

## State artefacts

- `guild/web/scripts/state/<program>.state.json` — latest run per program
- `guild/web/database/acg.db`, table `packml_runs` — full run history

Every run produces a `PackMLState` UDT instance with:
- `run_id` (epoch + uuid shard)
- `transitions` ordered list
- `pre_check_results` / `post_check_results`
- `terminal` (COMPLETE / ABORTED / HELD / STOPPED)
- `duration_s`

## Dashboards

L2 data is consumed by:

- `/api/health.json` (counts + last-updated)
- `build-programs.py` manifest (per-program last_state)
- Future: a `/guild/web/dashboard/` view showing PackML states

## Control rules

- A program in `ABORTED` does not block unrelated programs.
- `HELD` on pre-checks is silent success (pipeline skips the step).
- Post-check failure marks `ABORTED` and records the reason.
- Re-running a program always starts at `IDLE`; no sticky state.

## L2 does not

- Decide business rules (that's MES/L3).
- Store editorial content (that's L4 catalog).
- React to human events — only to L1 event signals.
