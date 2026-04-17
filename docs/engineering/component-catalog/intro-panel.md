# IntroPanel

Opening text panel with left border accent.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "IntroPanel",
    "tag": "section",
    "cssClass": "intro-panel",
    "description": "Opening content panel with accent left border, used at the top of index pages.",
    "category": "composite",
    "props": {
      "content": { "type": "String", "required": true }
    },
    "slots": ["default"],
    "template": "<section class=\"intro-panel\">{{ content }}</section>"
  },
  "tags": {
    "id": "intro-panel",
    "file_path": "guild/web/components/intro-panel.json",
    "dependencies": [],
    "used_by_views": ["white-paper-index", "members-index", "member-profile"],
    "schema_version": "1.0.0"
  }
}
```
