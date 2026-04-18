# Experiment UDT

A ritual experiment card — a time-boxed action with a falsifiable expectation.

## YAML

```yaml:udt:Experiment
name: Experiment
version: 1.0.0
fields:
  id:          { type: string, required: true }
  action:      { type: string, required: true, description: "What the practitioner does" }
  duration:    { type: string, required: true, description: "e.g., '90m', '2 weeks'" }
  expectation: { type: string, required: true, description: "Falsifiable predicted outcome" }
  context:     { type: string, required: false }
  author:      { type: string, required: false }
  tags:        { type: string-array, required: false }
```

## Python

```python:udt:Experiment
from dataclasses import dataclass, field

@dataclass
class Experiment:
    id: str
    action: str
    duration: str
    expectation: str
    context: str | None = None
    author: str | None = None
    tags: list[str] = field(default_factory=list)
```

## SQL

```sql:udt:Experiment
CREATE TABLE IF NOT EXISTS experiments (
    id          TEXT PRIMARY KEY,
    action      TEXT NOT NULL,
    duration    TEXT NOT NULL,
    expectation TEXT NOT NULL,
    context     TEXT,
    author      TEXT
);
```

## TypeScript

```typescript:udt:Experiment
export interface Experiment {
  id: string;
  action: string;
  duration: string;
  expectation: string;
  context?: string;
  author?: string;
  tags?: string[];
}
```

## JSON Schema

```json-schema:udt:Experiment
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "$id": "acg.udt.Experiment",
  "type": "object",
  "required": ["id","action","duration","expectation"],
  "properties": {
    "id":          {"type":"string"},
    "action":      {"type":"string"},
    "duration":    {"type":"string"},
    "expectation": {"type":"string"},
    "context":     {"type":"string"},
    "author":      {"type":"string"},
    "tags":        {"type":"array","items":{"type":"string"}}
  }
}
```

## Instance

```json:udt:Experiment
{
  "id": "ritual-09",
  "action": "Before publishing, run your draft through adversarial review",
  "duration": "1h per draft",
  "expectation": "At least one claim gets refuted, strengthening the remaining argument"
}
```
