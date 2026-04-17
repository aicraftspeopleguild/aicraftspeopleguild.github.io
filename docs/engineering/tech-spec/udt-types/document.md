# Document UDT

```json:udt:Template
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "udtType": "Document",
  "version": "1.0.0",
  "description": "An engineering document (URS, tech spec, architecture record).",
  "parameters": {
    "title":      { "dataType": "String",      "required": true },
    "doc_number": { "dataType": "String",      "required": false },
    "doc_type":   { "dataType": "String",      "required": true, "description": "urs | tech-spec | architecture | adr" },
    "version":    { "dataType": "String",      "required": false },
    "authors":    { "dataType": "StringArray", "required": false },
    "status":     { "dataType": "String",      "required": false, "default": "draft" },
    "summary":    { "dataType": "String",      "required": false },
    "tags":       { "dataType": "StringArray", "required": false }
  },
  "tags": {
    "id":             { "dataType": "String" },
    "source_path":    { "dataType": "String" },
    "schema_version": { "dataType": "String" }
  }
}
```
