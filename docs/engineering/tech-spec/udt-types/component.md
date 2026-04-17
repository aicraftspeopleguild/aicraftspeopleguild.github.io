# Component UDT

```json:udt:Template
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "udtType": "Component",
  "version": "1.0.0",
  "description": "A reusable UI component with typed props and slot definitions.",
  "parameters": {
    "name":        { "dataType": "String",      "required": true,  "description": "PascalCase component name" },
    "tag":         { "dataType": "String",      "required": false, "default": "div", "description": "HTML element tag" },
    "cssClass":    { "dataType": "String",      "required": false, "description": "Root CSS class(es)" },
    "description": { "dataType": "String",      "required": false },
    "category":    { "dataType": "String",      "required": false, "description": "atomic | composite | layout | page-level" },
    "props":       { "dataType": "JSON",        "required": false, "description": "Prop name → { type, required, default }" },
    "slots":       { "dataType": "StringArray", "required": false, "description": "Named insertion points for children" },
    "template":    { "dataType": "String",      "required": false, "description": "HTML template string with {{ prop }} bindings" }
  },
  "tags": {
    "id":             { "dataType": "String" },
    "file_path":      { "dataType": "String" },
    "dependencies":   { "dataType": "StringArray", "description": "Component IDs this depends on" },
    "used_by_views":  { "dataType": "StringArray", "description": "View IDs that use this component" },
    "schema_version": { "dataType": "String" }
  }
}
```
