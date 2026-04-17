# View UDT

```json:udt:Template
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "udtType": "View",
  "version": "1.0.0",
  "description": "A page-level component tree with data bindings.",
  "parameters": {
    "name":        { "dataType": "String",  "required": true },
    "description": { "dataType": "String",  "required": false },
    "root":        { "dataType": "JSON",    "required": true, "description": "Component tree root node" }
  },
  "tags": {
    "id":               { "dataType": "String" },
    "component_ids":    { "dataType": "StringArray", "description": "All components used in this view" },
    "data_sources":     { "dataType": "StringArray", "description": "JSON paths referenced by bindings" },
    "schema_version":   { "dataType": "String" }
  }
}
```
