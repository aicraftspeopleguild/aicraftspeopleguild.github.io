# RawHTML

Emits pre-rendered HTML content verbatim. Used as a bridge component while
page bodies are still authored as HTML strings (in views/data/*.data.json)
rather than fully decomposed component trees.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "RawHTML",
    "tag": "fragment",
    "cssClass": "",
    "description": "Emits a pre-rendered HTML string verbatim using the {{{ html }}} triple-brace (unescaped) syntax. Content lives in data files, not in HTML files.",
    "category": "layout",
    "props": {
      "html": { "type": "String", "required": true }
    },
    "slots": [],
    "template": "{{{ html }}}"
  },
  "tags": {
    "id": "raw-html",
    "file_path": "guild/web/components/raw-html.json",
    "dependencies": [],
    "used_by_views": ["charter", "flywheel", "mob-programming", "hall-of-fame", "hall-of-shame", "hushbell", "showcases"],
    "schema_version": "1.0.0"
  }
}
```
