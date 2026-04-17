# PageShell

The outermost page wrapper that every view uses.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "PageShell",
    "tag": "fragment",
    "cssClass": "",
    "description": "Logical page body wrapper. Emits <header> with guild-mark/title/subtitle/back-link, then <main class=\"container\">children</main>, then <footer>. The build.js wraps this with <!DOCTYPE html><html><head>...</head><body>[shell]</body></html>. The 'fragment' tag is a sentinel telling the renderer not to wrap output in an element.",
    "category": "page-level",
    "props": {
      "title":       { "type": "String",      "required": true },
      "bodyClass":   { "type": "String",      "required": false },
      "stylesheets": { "type": "StringArray", "required": false },
      "subtitle":    { "type": "String",      "required": false },
      "eyebrow":     { "type": "String",      "required": false },
      "backHref":    { "type": "URL",         "required": false },
      "backLabel":   { "type": "String",      "required": false },
      "meta":        { "type": "StringArray", "required": false }
    },
    "slots": ["default"],
    "template": "<header><div class=\"guild-mark\"><div class=\"emblem\">⚒ ACG ⚒</div></div>{{ #eyebrow }}<p class=\"eyebrow\">{{ eyebrow }}</p>{{ /eyebrow }}<h1>{{ title }}</h1>{{ #subtitle }}<p class=\"subtitle\">{{ subtitle }}</p>{{ /subtitle }}{{ #backHref }}<div class=\"back-link\"><a href=\"{{ backHref }}\">← {{ backLabel }}</a></div>{{ /backHref }}</header>\n<main class=\"container\">{{ slot:default }}</main>\n<footer><p>© 2026 AI Craftspeople Guild. Built by practitioners, not evangelists.</p><p><a href=\"https://github.com/aicraftspeopleguild\">GitHub</a></p></footer>"
  },
  "tags": {
    "id": "page-shell",
    "file_path": "guild/web/components/page-shell.json",
    "dependencies": ["page-header", "page-footer", "guild-mark"],
    "used_by_views": ["home", "white-paper-index", "white-paper-article", "members-index", "member-profile", "charter", "flywheel", "mob-programming", "hall-of-fame", "hall-of-shame"],
    "schema_version": "1.0.0"
  }
}
```
