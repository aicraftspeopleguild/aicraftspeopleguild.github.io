# Tag UDT

```json:udt:Template
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "udtType": "Tag",
  "version": "1.0.0",
  "description": "A topic tag that indexes entities.",
  "parameters": {
    "name":        { "dataType": "String", "required": true },
    "label":       { "dataType": "String", "required": false },
    "description": { "dataType": "String", "required": false }
  },
  "tags": {
    "paper_ids":    { "dataType": "StringArray" },
    "count":        { "dataType": "Int" },
    "last_updated": { "dataType": "String" }
  }
}
```
