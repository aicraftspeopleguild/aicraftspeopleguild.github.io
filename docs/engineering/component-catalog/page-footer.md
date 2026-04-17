# PageFooter

Standard site footer with GitHub link.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "PageFooter",
    "tag": "footer",
    "cssClass": "",
    "description": "Standard site footer with copyright, guild name, and GitHub link.",
    "category": "composite",
    "props": {
      "year":      { "type": "String", "required": false, "default": "2026" },
      "githubUrl": { "type": "URL",    "required": false, "default": "https://github.com/aicraftspeopleguild" }
    },
    "slots": [],
    "template": "<footer><p>© {{ year }} AI Craftspeople Guild. Built by practitioners, not evangelists.</p><p><a href=\"{{ githubUrl }}\">GitHub</a></p></footer>"
  },
  "tags": {
    "id": "page-footer",
    "file_path": "guild/web/components/page-footer.json",
    "dependencies": [],
    "used_by_views": ["page-shell"],
    "schema_version": "1.0.0"
  }
}
```
