# View Renderer Specification

**Document:** ACG-TS-003-2026
**Version:** 1.0.0

---

## 1. Purpose

The ACG View Renderer is a lightweight client-side engine that reads JSON view templates, resolves data bindings, and renders component trees to the DOM. It turns `index.html` into an SPA shell that dynamically serves all site pages from structured data.

## 2. Boot Sequence

```
┌─ index.html loads ─────────────────────────────┐
│  1. <link> stylesheets (style/main.css)        │
│  2. <div id="app"> mount point                 │
│  3. <script src="renderer.js">                 │
│  4. <script> ACGRenderer.init(config)          │
└────────────────────────────────────────────────┘
         │
         ▼
┌─ ACGRenderer.init() ──────────────────────────┐
│  1. Fetch site-map.json                       │
│  2. Fetch components/registry.json            │
│  3. Match current URL → Page entry            │
│  4. Fetch Page JSON → get view + data refs    │
│  5. Fetch View JSON + all data JSONs          │
│  6. Walk view tree, render to #app            │
└───────────────────────────────────────────────┘
```

## 3. Configuration

```json
{
  "siteMap":       "guild/web/site-map.json",
  "components":    "guild/web/components/registry.json",
  "mountPoint":    "#app",
  "basePath":      "/",
  "fallbackPage":  "pages/404.page.json",
  "analyticsId":   "G-Z1CEF69ZSH"
}
```

## 4. Rendering Algorithm

### 4.1 Tree Walk

```
function renderNode(node, context):
    // Conditional check
    if node.when exists:
        value = resolve(node.when, context)
        if falsy(value): return null

    // Resolve props
    boundProps = {}
    for key, val in node.props:
        boundProps[key] = resolve(val, context)

    // Look up component definition
    comp = registry[node.type]

    // Create DOM element
    el = createElement(comp.tag)
    el.className = resolveClasses(comp.cssClass, boundProps)

    // Render template or children
    if comp.template:
        el.innerHTML = interpolate(comp.template, boundProps)
    else if node.children:
        for child in node.children:
            childEl = renderNode(child, context)
            if childEl: el.appendChild(childEl)

    // Handle repeat blocks
    if node.repeat:
        items = resolve(node.repeat.source, context)
        for item in items:
            childContext = { ...context, [node.repeat.as]: item }
            childEl = renderNode(node.repeat.template, childContext)
            if childEl: el.appendChild(childEl)

    return el
```

### 4.2 Binding Resolution

Bindings use `{{ path.to.value }}` syntax:

```
resolve("{{ paper.title }}", { paper: { title: "AI Harness" } })
→ "AI Harness"

resolve("{{ paper.authors }}", { paper: { authors: ["Alex"] } })
→ ["Alex"]  (array preserved for iteration)

resolve("static text", context)
→ "static text"  (no {{ }} → passthrough)
```

Nested paths supported: `{{ paper.tags.0 }}` accesses first tag.

### 4.3 Template Interpolation

Mustache-lite syntax inside component `template` strings:

| Syntax | Meaning |
|--------|---------|
| `{{ prop }}` | Insert value |
| `{{ #prop }}...{{ /prop }}` | Conditional block (truthy) |
| `{{ ^prop }}...{{ /prop }}` | Inverted block (falsy) |
| `{{ #array }}...{{ . }}...{{ /array }}` | Iterate array, `{{ . }}` = current item |
| `{{ slot:name }}` | Insert named slot children |

## 5. Router

### 5.1 URL Matching

The router matches the browser's `location.pathname` against `site-map.json` routes:

```
/                           → home
/guild/web/white-papers     → white-paper-index
/guild/web/white-papers/ai-harness → white-paper-article (slug=ai-harness)
/guild/web/members          → members-index
/guild/web/members/alex-bunardzic  → member-profile (slug=alex-bunardzic)
```

### 5.2 Dynamic Routes

Routes with `:slug` are resolved against UDT instance IDs:

```json
{
  "path": "/white-papers/:slug",
  "page": "pages/white-paper-article.page.json",
  "dynamic": true
}
```

The renderer loads the instance at `white-papers/udts/instances/{slug}.json` and merges it into the data context.

### 5.3 Navigation

Internal links use `data-route` attributes for SPA navigation:

```html
<a href="/guild/web/white-papers/ai-harness" data-route>Read White Paper</a>
```

The renderer intercepts clicks on `[data-route]` links, pushes history state, and re-renders without full page reload.

Links without `data-route` navigate normally (external links, downloads).

## 6. Fallback Strategy

### 6.1 No-JS Mode

Without JavaScript, `index.html` shows a minimal landing page with links to all static HTML files. Every page under `guild/web/` remains a standalone HTML file that works without the renderer.

### 6.2 404 Handling

Unmatched routes render `pages/404.page.json` — a simple view with a "page not found" message and navigation back to home.

### 6.3 Loading States

While fetching view/data JSONs, the renderer shows a minimal loading indicator in `#app`:

```html
<div class="loading">
  <div class="emblem">⚒ ACG ⚒</div>
  <p>Loading...</p>
</div>
```

## 7. UDT Instance

```json:udt:Document
{
  "udtType": "Document",
  "parameters": {
    "title": "View Renderer Specification",
    "doc_number": "ACG-TS-003-2026",
    "doc_type": "tech-spec",
    "version": "1.0.0",
    "authors": ["Thomas Frumkin"],
    "status": "draft",
    "summary": "Specification for the ACG client-side view renderer covering boot sequence, tree walk algorithm, binding resolution, mustache-lite template syntax, SPA router, and fallback strategy.",
    "tags": ["renderer", "spa", "views", "router", "templates"]
  },
  "tags": {
    "id": "acg-ts-003-2026",
    "source_path": "docs/engineering/tech-spec/renderer.md",
    "schema_version": "1.0.0"
  }
}
```
