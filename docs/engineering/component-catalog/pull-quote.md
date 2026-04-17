# PullQuote

Emphasized quote with attribution.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "PullQuote",
    "tag": "div",
    "cssClass": "pull-quote",
    "description": "Highlighted quote block with rust left border and serif font.",
    "category": "atomic",
    "props": {
      "text":        { "type": "String", "required": true },
      "attribution": { "type": "String", "required": false }
    },
    "slots": [],
    "template": "<div class=\"pull-quote\">\"{{ text }}\" — {{ attribution }}</div>"
  },
  "tags": {
    "id": "pull-quote",
    "file_path": "guild/web/components/pull-quote.json",
    "dependencies": [],
    "used_by_views": ["white-paper-article", "mob-programming"],
    "schema_version": "1.0.0"
  }
}
```
