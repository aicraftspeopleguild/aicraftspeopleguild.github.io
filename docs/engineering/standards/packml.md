---
acg-paper:
  id: ACG-STD-PACKML-2026
  type: standard
  title: "ACG PackML Process Standard"
  author: "AI Craftspeople Guild"
  date: 2026-04-18
  status: published
  tags: [packml, isa-95, state-machine, scada]
  abstract: >
    Every automated build pipeline step runs through ISA-TR88.00.02 PackML
    core states with pre/post checks. Defines the state enum, transition
    rules, check semantics, and persistence contract.
---

# ACG PackML Process Standard

Each build-pipeline script is a `Process` wrapped by the state machine in `guild/web/scripts/lib/packml_process.py`.

## Core states

```
IDLE → STARTING → EXECUTE → COMPLETING → COMPLETE  (happy path)
                               ↓
                           ABORTING → ABORTED      (exception or post-check fail)

IDLE → STARTING → HELD                             (pre-check fail — work skipped)
```

Terminal states: **COMPLETE**, **ABORTED**, **HELD**, **STOPPED**.

## Transition rules

| From        | To          | Trigger                                    |
|-------------|-------------|--------------------------------------------|
| IDLE        | STARTING    | Context manager `__enter__`                |
| STARTING    | HELD        | Any pre-check returns False / raises       |
| STARTING    | EXECUTE     | All pre-checks pass                        |
| EXECUTE     | ABORTING    | User code raises exception                 |
| EXECUTE     | COMPLETING  | User code returns cleanly                  |
| COMPLETING  | ABORTING    | Any post-check fails                       |
| COMPLETING  | COMPLETE    | All post-checks pass                       |
| ABORTING    | ABORTED     | Terminal after failure                     |

## Check contract

A check is a zero-arg callable:
- Returns `True` / `None` — pass
- Returns `False` — fail (no reason captured)
- Raises `CheckFailed(msg)` — fail with reason
- Raises anything else — fail with exception type + message

Prebuilt helpers: `path_exists(p)`, `has_files(glob, min_count)`.

## Persistence contract

After every run, a `PackMLState` UDT instance is written to
`guild/web/scripts/state/<program_id>.state.json`:

```json:udt:PackMLState
{
  "udtType": "PackMLState",
  "parameters": {
    "program_id": "components--build-catalog_py",
    "run_id": "1745000000-abc123",
    "started_at": "2026-04-18T00:00:00Z",
    "ended_at":   "2026-04-18T00:00:00Z",
    "terminal":   "COMPLETE",
    "transitions": [
      {"state":"STARTING","at":"...","note":"running pre_checks"}
    ],
    "pre_check_results":  {"path_exists(instances)": {"ok":true,"note":""}},
    "post_check_results": {"has_files(*.json)": {"ok":true,"note":""}},
    "error": null
  },
  "tags": {
    "id": "components--build-catalog_py-1745000000-abc123",
    "duration_s": "0.004",
    "schema_version": "1.0.0"
  }
}
```

The SQLite `packml_runs` table (L4) mirrors the same rows for querying
across the full run history.

## Invariants

- A process always starts at `IDLE`; no sticky state between runs.
- State writes are atomic (single `write_text` call per run).
- `duration_s` is always populated — from wall clock, not per-state sum.
- Re-running a COMPLETE process overwrites its previous state record.
