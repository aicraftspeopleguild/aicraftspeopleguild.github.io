# StaticHTMLFrame

Embeds a pre-rendered HTML page as an iframe. Fallback for routes that have no Renderer-compatible JSON view — used for legacy whitepapers, slide decks, and external HTML assets served directly from the repo.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "StaticHTMLFrame",
    "tag": "div",
    "cssClass": "static-html-frame",
    "description": "Embeds a pre-rendered HTML page as an iframe. Fallback for routes that have no JSON view.",
    "category": "utility",
    "props": {
      "src":    { "type": "URL",    "required": true,  "description": "Path to the HTML file to embed" },
      "title":  { "type": "String", "required": true,  "description": "Accessible iframe title" },
      "height": { "type": "String", "required": false, "default": "100vh" }
    },
    "slots": [],
    "template": "<div class=\"static-html-frame\"><iframe src=\"{{ src }}\" title=\"{{ title }}\" style=\"width:100%;height:{{ height }};border:none;\"></iframe></div>"
  },
  "tags": {
    "id": "static-html-frame",
    "file_path": "guild/Enterprise/L2/hmi/web/components/static-html-frame.json",
    "dependencies": [],
    "used_by_views": [],
    "schema_version": "1.0.0"
  }
}
```
