# StaticHTMLFrame

Embeds a pre-rendered HTML page as an iframe. Fallback for routes that have
not yet been decomposed.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "StaticHTMLFrame",
    "tag": "iframe",
    "cssClass": "static-html-frame",
    "description": "Embeds a pre-rendered HTML page as an iframe.",
    "category": "layout",
    "props": {
      "src":   { "type": "URL",    "required": true },
      "title": { "type": "String", "required": false }
    },
    "slots": [],
    "template": ""
  },
  "tags": {
    "id": "static-html-frame",
    "file_path": "guild/web/components/static-html-frame.json",
    "dependencies": [],
    "used_by_views": ["static-page"],
    "schema_version": "1.0.0"
  }
}
```
