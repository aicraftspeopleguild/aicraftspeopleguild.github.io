# Page UDT

```json:udt:Template
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "udtType": "Page",
  "version": "1.0.0",
  "description": "A route entry binding a URL path to a view and data sources.",
  "parameters": {
    "title":       { "dataType": "String",      "required": true },
    "slug":        { "dataType": "String",      "required": true },
    "route":       { "dataType": "String",      "required": true, "description": "URL path pattern" },
    "view":        { "dataType": "String",      "required": true, "description": "Path to view.json" },
    "data":        { "dataType": "JSON",        "required": false, "description": "Named data source paths" },
    "stylesheets": { "dataType": "StringArray", "required": false },
    "section":     { "dataType": "String",      "required": false },
    "parent_slug": { "dataType": "String",      "required": false },
    "status":      { "dataType": "String",      "required": false, "default": "published" }
  },
  "tags": {
    "id":             { "dataType": "String" },
    "view_id":        { "dataType": "String" },
    "schema_version": { "dataType": "String" }
  }
}
```
