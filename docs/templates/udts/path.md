# Path UDT

A `path.json` entry — describes one node in the site-map tree and carries metadata for the renderer's navigation graph.

## YAML

```yaml:udt:Path
name: Path
version: 1.0.0
fields:
  id:       { type: string, required: true,  description: "Dot-separated path identifier, e.g. guild.web.home" }
  label:    { type: string, required: true }
  slug:     { type: string, required: false, description: "URL slug override; defaults to last id segment" }
  parent:   { type: string, required: false, description: "Parent path id" }
  children: { type: string-array, required: false }
  view:     { type: string, required: false }
  data:     { type: object, required: false }
```

## Python

```python:udt:Path
from dataclasses import dataclass, field

@dataclass
class Path:
    id: str
    label: str
    slug: str | None = None
    parent: str | None = None
    children: list[str] = field(default_factory=list)
    view: str | None = None
    data: dict = field(default_factory=dict)
```

## JSON Schema

```json-schema:udt:Path
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["id", "label"],
  "properties": {
    "id":       { "type": "string" },
    "label":    { "type": "string" },
    "slug":     { "type": "string" },
    "parent":   { "type": "string" },
    "children": { "type": "array", "items": { "type": "string" } },
    "view":     { "type": "string" },
    "data":     { "type": "object" }
  }
}
```
