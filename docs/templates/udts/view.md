# View UDT

A Perspective-style JSON view — a tree of component bindings that the renderer walks to produce the DOM.

## YAML

```yaml:udt:View
name: View
version: 1.0.0
fields:
  id:       { type: string, required: true,  description: "kebab-case view identifier" }
  title:    { type: string, required: false }
  root:     { type: object, required: true,  description: "Root ViewNode" }
  data:     { type: object, required: false, description: "Named data source refs" }
  params:   { type: object, required: false, description: "URL / context params" }
```

## Python

```python:udt:View
from dataclasses import dataclass, field

@dataclass
class View:
    id: str
    root: dict
    title: str | None = None
    data: dict = field(default_factory=dict)
    params: dict = field(default_factory=dict)
```

## JSON Schema

```json-schema:udt:View
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["id", "root"],
  "properties": {
    "id":     { "type": "string", "pattern": "^[a-z][a-z0-9-]*$" },
    "title":  { "type": "string" },
    "root":   { "type": "object" },
    "data":   { "type": "object" },
    "params": { "type": "object" }
  }
}
```
