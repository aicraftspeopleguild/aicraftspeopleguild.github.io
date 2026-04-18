# PackMLState UDT

A single state-machine run record — captures the entry state, exit state, timestamps, and any error payload for one PackML transition.

## YAML

```yaml:udt:PackMLState
name: PackMLState
version: 1.0.0
fields:
  program_id:   { type: string, required: true }
  run_id:       { type: string, required: true,  description: "UUID for this execution" }
  state:        { type: enum,   required: true,  values: [IDLE, STARTING, EXECUTE, COMPLETING, COMPLETE, HOLDING, HELD, UNHOLDING, SUSPENDING, SUSPENDED, UNSUSPENDING, STOPPING, STOPPED, ABORTING, ABORTED, CLEARING] }
  prev_state:   { type: string, required: false }
  entered_at:   { type: string, required: true,  format: iso8601 }
  exited_at:    { type: string, required: false, format: iso8601 }
  error:        { type: string, required: false }
  context:      { type: object, required: false }
```

## Python

```python:udt:PackMLState
from dataclasses import dataclass, field
from typing import Literal

State = Literal[
    "IDLE","STARTING","EXECUTE","COMPLETING","COMPLETE",
    "HOLDING","HELD","UNHOLDING",
    "SUSPENDING","SUSPENDED","UNSUSPENDING",
    "STOPPING","STOPPED","ABORTING","ABORTED","CLEARING",
]

@dataclass
class PackMLState:
    program_id: str
    run_id: str
    state: State
    entered_at: str
    prev_state: str | None = None
    exited_at: str | None = None
    error: str | None = None
    context: dict = field(default_factory=dict)
```

## SQL

```sql:udt:PackMLState
CREATE TABLE IF NOT EXISTS packml_states (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    program_id  TEXT NOT NULL,
    run_id      TEXT NOT NULL,
    state       TEXT NOT NULL,
    prev_state  TEXT,
    entered_at  TEXT NOT NULL,
    exited_at   TEXT,
    error       TEXT,
    context     TEXT  -- JSON blob
);
```
