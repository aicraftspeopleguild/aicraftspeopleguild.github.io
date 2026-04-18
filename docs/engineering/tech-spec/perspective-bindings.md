# Perspective Bindings

Bindings live in `propConfig`. Key is the dotted path to the target
property (e.g. `props.text`), value is the binding descriptor.

## Property binding

Reads a value from the view context. Path is dotted into `view.params.*`,
`view.custom.*`, or `view.props.*`.

```json
"propConfig": {
  "props.text": {
    "binding": {
      "type": "property",
      "config": { "path": "view.params.title" }
    }
  }
}
```

## Expression binding

Simple expression against the context. Supports `{path}` substitution.

```json
"propConfig": {
  "props.html": {
    "binding": {
      "type": "expression",
      "config": { "expression": "\"<h2>\" + {view.params.title} + \"</h2>\"" }
    }
  }
}
```

## Data binding (maps to data source)

Binds to a loaded Page data source by key. Same mechanism as Perspective's
tag/query bindings but resolved from static JSON files at build time.

```json
"propConfig": {
  "props.items": {
    "binding": {
      "type": "data",
      "config": { "source": "papers", "path": "$" }
    }
  }
}
```

`config.path` uses a minimal JSONPath subset:
- `$` — root of the source
- `$.field` — field access
- `$[0]` — array index
- `$[*].title` — array map (for loops)

## Binding resolution order

1. Default prop value from `props.*`
2. Binding from `propConfig` overrides the default
3. Parent scope values bleed through (e.g., parent's repeat variable)

Bindings are resolved lazily per render, before child recursion.
