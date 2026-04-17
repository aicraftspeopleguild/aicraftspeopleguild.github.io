# CTASection

Call-to-action section with rotating gradient background.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "CTASection",
    "tag": "section",
    "cssClass": "cta-section",
    "description": "Call-to-action section with rotating gradient background and primary/secondary buttons.",
    "category": "composite",
    "props": {
      "heading":       { "type": "String", "required": true },
      "description":   { "type": "String", "required": false },
      "primaryText":   { "type": "String", "required": false },
      "primaryHref":   { "type": "URL",    "required": false },
      "secondaryText": { "type": "String", "required": false },
      "secondaryHref": { "type": "URL",    "required": false }
    },
    "slots": [],
    "template": "<section class=\"cta-section\"><h2>{{ heading }}</h2>{{ #description }}<p>{{ description }}</p>{{ /description }}<div class=\"cta-actions\">{{ #primaryHref }}<a href=\"{{ primaryHref }}\" class=\"btn btn-primary\">{{ primaryText }}</a>{{ /primaryHref }}{{ #secondaryHref }}<a href=\"{{ secondaryHref }}\" class=\"btn btn-secondary\">{{ secondaryText }}</a>{{ /secondaryHref }}</div></section>"
  },
  "tags": {
    "id": "cta-section",
    "file_path": "guild/web/components/cta-section.json",
    "dependencies": ["button"],
    "used_by_views": ["page-shell", "home", "white-paper-index", "members-index"],
    "schema_version": "1.0.0"
  }
}
```
