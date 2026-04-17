# Callout

Bordered note block for important information.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "Callout",
    "tag": "div",
    "cssClass": "callout",
    "description": "Left-bordered callout block for important contextual notes.",
    "category": "atomic",
    "props": {
      "content": { "type": "String", "required": true }
    },
    "slots": [],
    "template": "<div class=\"callout\"><p>{{ content }}</p></div>"
  },
  "tags": {
    "id": "callout",
    "file_path": "guild/web/components/callout.json",
    "dependencies": [],
    "used_by_views": ["white-paper-article"],
    "schema_version": "1.0.0"
  }
}
```
