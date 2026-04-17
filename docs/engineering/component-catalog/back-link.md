# BackLink

Navigation link back to parent page.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "BackLink",
    "tag": "div",
    "cssClass": "back-link",
    "description": "Header navigation link with left arrow to parent page.",
    "category": "atomic",
    "props": {
      "href":  { "type": "URL",    "required": true },
      "label": { "type": "String", "required": true }
    },
    "slots": [],
    "template": "<div class=\"back-link\"><a href=\"{{ href }}\">← {{ label }}</a></div>"
  },
  "tags": {
    "id": "back-link",
    "file_path": "guild/web/components/back-link.json",
    "dependencies": [],
    "used_by_views": ["page-shell"],
    "schema_version": "1.0.0"
  }
}
```
