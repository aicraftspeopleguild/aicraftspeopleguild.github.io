# Eyebrow

Small uppercase label above headings.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "Eyebrow",
    "tag": "p",
    "cssClass": "eyebrow",
    "description": "Small uppercase label used above page titles for context.",
    "category": "atomic",
    "props": {
      "text": { "type": "String", "required": true }
    },
    "slots": [],
    "template": "<p class=\"eyebrow\">{{ text }}</p>"
  },
  "tags": {
    "id": "eyebrow",
    "file_path": "guild/web/components/eyebrow.json",
    "dependencies": [],
    "used_by_views": ["page-header", "member-profile", "white-paper-article"],
    "schema_version": "1.0.0"
  }
}
```
