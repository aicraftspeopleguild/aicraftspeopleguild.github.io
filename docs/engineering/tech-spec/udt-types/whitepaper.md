# WhitePaper UDT

```json:udt:Template
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "udtType": "WhitePaper",
  "version": "1.0.0",
  "description": "A Guild white paper, position paper, or research publication.",
  "parameters": {
    "title":            { "dataType": "String",      "required": true },
    "authors":          { "dataType": "StringArray",  "required": true },
    "publication_date": { "dataType": "String",      "required": false },
    "doc_number":       { "dataType": "String",      "required": false },
    "source_medium":    { "dataType": "String",      "required": false },
    "summary":          { "dataType": "String",      "required": false },
    "tags":             { "dataType": "StringArray",  "required": false },
    "status":           { "dataType": "String",      "required": false, "default": "published" },
    "site_href":        { "dataType": "String",      "required": false }
  },
  "tags": {
    "id":                    { "dataType": "String" },
    "original_path":         { "dataType": "String" },
    "original_format":       { "dataType": "String" },
    "original_hash_sha256":  { "dataType": "String" },
    "body":                  { "dataType": "String" },
    "instance_path":         { "dataType": "String" },
    "ingested_at":           { "dataType": "String" },
    "schema_version":        { "dataType": "String" }
  }
}
```
