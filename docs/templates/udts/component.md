# Component UDT

A reusable UI component registered in the ACG component registry.

## YAML

```yaml:udt:Component
name: Component
version: 1.0.0
fields:
  id:          { type: string,       required: true,  description: "kebab-case identifier matching the JSON filename" }
  name:        { type: string,       required: true,  description: "PascalCase display name" }
  tag:         { type: string,       required: true,  description: "Root HTML tag emitted" }
  cssClass:    { type: string,       required: true,  description: "BEM block class" }
  description: { type: string,       required: true }
  category:    { type: enum,         required: true,  values: [atomic, composite, layout, utility] }
  props:       { type: object,       required: false, description: "Named prop definitions" }
  slots:       { type: string-array, required: false }
  template:    { type: string,       required: true,  description: "Mustache HTML template" }
  dependencies:    { type: string-array, required: false }
  used_by_views:   { type: string-array, required: false }
  schema_version:  { type: string,       required: true }
```

## Python

```python:udt:Component
from dataclasses import dataclass, field
from typing import Literal
Category = Literal["atomic", "composite", "layout", "utility"]

@dataclass
class Component:
    id: str
    name: str
    tag: str
    css_class: str
    description: str
    category: Category
    template: str
    schema_version: str
    props: dict = field(default_factory=dict)
    slots: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    used_by_views: list[str] = field(default_factory=list)
```

## JSON Schema

```json-schema:udt:Component
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["id", "name", "tag", "cssClass", "description", "category", "template", "schema_version"],
  "properties": {
    "id":           { "type": "string", "pattern": "^[a-z][a-z0-9-]*$" },
    "name":         { "type": "string" },
    "tag":          { "type": "string" },
    "cssClass":     { "type": "string" },
    "description":  { "type": "string" },
    "category":     { "type": "string", "enum": ["atomic","composite","layout","utility"] },
    "template":     { "type": "string" },
    "schema_version": { "type": "string" }
  }
}
```
