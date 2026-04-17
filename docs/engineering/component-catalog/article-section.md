# ArticleSection

Content section within a white paper.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "ArticleSection",
    "tag": "section",
    "cssClass": "section",
    "description": "Content section with heading, body text, and optional sub-components (callouts, figures, code blocks).",
    "category": "composite",
    "props": {
      "id":    { "type": "String", "required": true },
      "title": { "type": "String", "required": true }
    },
    "slots": ["default"],
    "template": "<section id=\"{{ id }}\" class=\"section\"><h2>{{ title }}</h2>{{ slot:default }}</section>"
  },
  "tags": {
    "id": "article-section",
    "file_path": "guild/web/components/article-section.json",
    "dependencies": [],
    "used_by_views": ["white-paper-article"],
    "schema_version": "1.0.0"
  }
}
```
