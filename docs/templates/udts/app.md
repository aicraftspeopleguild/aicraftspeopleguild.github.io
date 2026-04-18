# App UDT

An addressable render unit — a self-contained mini-app that bundles a view, its data sources, and routing metadata into one deployable entry.

## YAML

```yaml:udt:App
name: App
version: 1.0.0
fields:
  id:       { type: string, required: true,  description: "kebab-case app identifier" }
  title:    { type: string, required: true }
  slug:     { type: string, required: true,  description: "Mount-point URL path" }
  entry:    { type: string, required: true,  description: "View ID or HTML file path" }
  data:     { type: object, required: false, description: "Named data source URLs" }
  meta:     { type: object, required: false }
  static:   { type: boolean, required: false, default: false, description: "True → served as pre-rendered HTML" }
```

## Python

```python:udt:App
from dataclasses import dataclass, field

@dataclass
class App:
    id: str
    title: str
    slug: str
    entry: str
    data: dict = field(default_factory=dict)
    meta: dict = field(default_factory=dict)
    static: bool = False
```

## JSON Schema

```json-schema:udt:App
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["id", "title", "slug", "entry"],
  "properties": {
    "id":     { "type": "string", "pattern": "^[a-z][a-z0-9-]*$" },
    "title":  { "type": "string" },
    "slug":   { "type": "string" },
    "entry":  { "type": "string" },
    "data":   { "type": "object" },
    "meta":   { "type": "object" },
    "static": { "type": "boolean" }
  }
}
```
