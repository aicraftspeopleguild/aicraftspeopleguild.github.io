# Perspective-Compatible View Schema

**Document:** ACG-TS-004-2026  **Version:** 1.0.0

The ACG site adopts Ignition Perspective's view/component JSON schema so
views can be authored in any Perspective-aware tool and rendered by our
builder. Components live in an `acg.*` namespace, mirroring Perspective's
`ia.*` naming convention.

## View Schema

```json
{
  "custom": {},
  "params": {
    "title": { "dataType": "String" }
  },
  "propConfig": {
    "props.defaultTitle": {
      "binding": { "type": "property", "config": { "path": "view.params.title" } }
    }
  },
  "props": {
    "defaultTitle": ""
  },
  "root": {
    "meta": { "name": "root" },
    "type": "acg.container.page",
    "props": {},
    "propConfig": {},
    "children": []
  }
}
```

| Key          | Purpose                                                  |
|--------------|----------------------------------------------------------|
| `custom`     | View-author-defined properties                           |
| `params`     | Typed view inputs (set by Page when rendering)           |
| `propConfig` | Bindings (property, expression, query, tag, view)        |
| `props`      | Default prop values                                      |
| `root`       | Root component tree node                                 |

## Component Node Schema

```json
{
  "meta": { "name": "Title" },
  "type": "acg.display.heading",
  "position": { "basis": "auto" },
  "props": { "text": "Hello", "level": 1 },
  "propConfig": {
    "props.text": {
      "binding": { "type": "property", "config": { "path": "view.params.title" } }
    }
  },
  "children": []
}
```

See:
- [Component Types](perspective-components.md)
- [Bindings](perspective-bindings.md)
- [Renderer](perspective-renderer.md)
