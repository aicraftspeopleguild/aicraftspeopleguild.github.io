# PageHeader

Full page header with guild mark, title, subtitle, and optional back-link.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "PageHeader",
    "tag": "header",
    "cssClass": "",
    "description": "Full page header assembling GuildMark, title, subtitle, eyebrow, article-meta, and BackLink.",
    "category": "composite",
    "props": {
      "title":       { "type": "String",      "required": true },
      "subtitle":    { "type": "String",      "required": false },
      "eyebrow":     { "type": "String",      "required": false },
      "backHref":    { "type": "URL",         "required": false },
      "backLabel":   { "type": "String",      "required": false },
      "meta":        { "type": "StringArray", "required": false, "description": "Article metadata badges" }
    },
    "slots": [],
    "template": "<header><div class=\"guild-mark\"><div class=\"emblem\">⚒ ACG ⚒</div></div>{{ #eyebrow }}<p class=\"eyebrow\">{{ eyebrow }}</p>{{ /eyebrow }}<h1>{{ title }}</h1>{{ #subtitle }}<p class=\"subtitle\">{{ subtitle }}</p>{{ /subtitle }}{{ #meta }}<div class=\"article-meta\">{{ #meta }}<span>{{ . }}</span>{{ /meta }}</div>{{ /meta }}{{ #backHref }}<div class=\"back-link\"><a href=\"{{ backHref }}\">← {{ backLabel }}</a></div>{{ /backHref }}</header>"
  },
  "tags": {
    "id": "page-header",
    "file_path": "guild/web/components/page-header.json",
    "dependencies": ["guild-mark", "eyebrow", "back-link"],
    "used_by_views": ["page-shell"],
    "schema_version": "1.0.0"
  }
}
```
