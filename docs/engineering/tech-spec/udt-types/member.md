# Member UDT

```json:udt:Template
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "udtType": "Member",
  "version": "1.0.0",
  "description": "A Guild member profile.",
  "parameters": {
    "name":           { "dataType": "String",      "required": true },
    "role":           { "dataType": "String",      "required": false, "description": "founder | core | contributor | advisor" },
    "title":          { "dataType": "String",      "required": false, "description": "Professional title" },
    "bio":            { "dataType": "String",      "required": false },
    "avatar_href":    { "dataType": "String",      "required": false },
    "expertise_tags": { "dataType": "StringArray", "required": false },
    "links":          { "dataType": "JSON",        "required": false, "description": "{ github, linkedin, website }" },
    "joined_date":    { "dataType": "String",      "required": false }
  },
  "tags": {
    "id":              { "dataType": "String" },
    "slug":            { "dataType": "String" },
    "paper_ids":       { "dataType": "StringArray", "description": "Papers this member authored" },
    "instance_path":   { "dataType": "String" },
    "schema_version":  { "dataType": "String" }
  }
}
```
