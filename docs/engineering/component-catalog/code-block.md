# CodeBlock

Syntax-highlighted code display.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "CodeBlock",
    "tag": "pre",
    "cssClass": "code-block",
    "description": "Dark-background code display with monospace font.",
    "category": "atomic",
    "props": {
      "code":     { "type": "String", "required": true },
      "language": { "type": "String", "required": false }
    },
    "slots": [],
    "template": "<pre class=\"code-block\"><code class=\"lang-{{ language }}\">{{ code }}</code></pre>"
  },
  "tags": {
    "id": "code-block",
    "file_path": "guild/web/components/code-block.json",
    "dependencies": [],
    "used_by_views": ["white-paper-article"],
    "schema_version": "1.0.0"
  }
}
```
