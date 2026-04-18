# Tag UDT

An Ignition-style tag with quality and timestamp semantics. Used for routing, topics, and runtime state.

## YAML

```yaml:udt:Tag
name: Tag
version: 1.0.0
fields:
  path:    { type: string, required: true, description: "Slash-delimited identifier" }
  value:   { type: any,    required: false }
  quality: { type: enum,   required: false, values: [good, stale, bad], default: good }
  ts:      { type: int,    required: false, description: "Epoch milliseconds" }
```

## Python

```python:udt:Tag
from dataclasses import dataclass
from typing import Any, Literal
Quality = Literal["good","stale","bad"]

@dataclass
class Tag:
    path: str
    value: Any = None
    quality: Quality = "good"
    ts: int | None = None
```

## SQL

```sql:udt:Tag
CREATE TABLE IF NOT EXISTS tags (
    path    TEXT PRIMARY KEY,
    value   TEXT,
    quality TEXT NOT NULL DEFAULT 'good'
            CHECK(quality IN ('good','stale','bad')),
    ts      INTEGER
);
```

## TypeScript

```typescript:udt:Tag
export type Quality = "good" | "stale" | "bad";
export interface Tag {
  path: string;
  value?: unknown;
  quality?: Quality;
  ts?: number;
}
```

## JSON Schema

```json-schema:udt:Tag
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "$id": "acg.udt.Tag",
  "type": "object",
  "required": ["path"],
  "properties": {
    "path":    {"type":"string"},
    "value":   {},
    "quality": {"enum":["good","stale","bad"],"default":"good"},
    "ts":      {"type":"integer"}
  }
}
```

## Instance

```json:udt:Tag
{ "path": "plant/line1/state", "value": "RUNNING", "quality": "good", "ts": 1745000000000 }
```
