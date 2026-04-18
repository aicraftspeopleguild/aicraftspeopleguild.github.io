# Page UDT

A route binding — maps a URL slug to a view and its data sources.

## YAML

```yaml:udt:Page
name: Page
version: 1.0.0
fields:
  slug:     { type: string, required: true,  description: "URL path segment(s), no leading slash" }
  title:    { type: string, required: true }
  view:     { type: string, required: true,  description: "View ID resolved from registry" }
  data:     { type: object, required: false, description: "Named data source URLs" }
  meta:     { type: object, required: false, description: "Open Graph / SEO metadata" }
```

## Python

```python:udt:Page
from dataclasses import dataclass, field

@dataclass
class Page:
    slug: str
    title: str
    view: str
    data: dict = field(default_factory=dict)
    meta: dict = field(default_factory=dict)
```

## JSON Schema

```json-schema:udt:Page
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["slug", "title", "view"],
  "properties": {
    "slug":  { "type": "string" },
    "title": { "type": "string" },
    "view":  { "type": "string" },
    "data":  { "type": "object" },
    "meta":  { "type": "object" }
  }
}
```
