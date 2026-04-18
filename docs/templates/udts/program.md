# Program UDT

A build pipeline program — a named, executable unit in the ACG tool runner with PackML state-machine supervision.

## YAML

```yaml:udt:Program
name: Program
version: 1.0.0
fields:
  id:          { type: string, required: true,  description: "kebab-case identifier" }
  label:       { type: string, required: true }
  category:    { type: enum,   required: true,  values: [generate, build, ingest, deploy, test, validate] }
  description: { type: string, required: false }
  script:      { type: string, required: true,  description: "Repo-relative path to the entry script" }
  inputs:      { type: string-array, required: false }
  outputs:     { type: string-array, required: false }
  pre_checks:  { type: string-array, required: false }
  post_checks: { type: string-array, required: false }
```

## Python

```python:udt:Program
from dataclasses import dataclass, field
from typing import Literal
Category = Literal["generate","build","ingest","deploy","test","validate"]

@dataclass
class Program:
    id: str
    label: str
    category: Category
    script: str
    description: str | None = None
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    pre_checks: list[str] = field(default_factory=list)
    post_checks: list[str] = field(default_factory=list)
```

## JSON Schema

```json-schema:udt:Program
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["id", "label", "category", "script"],
  "properties": {
    "id":       { "type": "string", "pattern": "^[a-z][a-z0-9-]*$" },
    "label":    { "type": "string" },
    "category": { "type": "string", "enum": ["generate","build","ingest","deploy","test","validate"] },
    "script":   { "type": "string" }
  }
}
```
