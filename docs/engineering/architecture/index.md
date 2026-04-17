# System Architecture — ACG Guild Site

**Document:** ACG-ARCH-001-2026
**Version:** 1.0.0
**Status:** Draft

---

## 1. Overview

The ACG site is a static GitHub Pages site that uses a UDT-driven component architecture inspired by Ignition Perspective. Content is authored as source files (Markdown, CSV), ingested into typed JSON instances, and rendered through a lightweight client-side view engine that maps component trees to DOM.

```
┌─────────────────────────────────────────────────┐
│                  Source Layer                    │
│  originals/*.md  originals/*.csv  *.html        │
└──────────────────────┬──────────────────────────┘
                       │ ingest.py
                       ▼
┌─────────────────────────────────────────────────┐
│                Instance Layer                    │
│  udts/instances/*.json    tags/index.json        │
│  site-map.json            views/*.view.json      │
└──────────────────────┬──────────────────────────┘
                       │ renderer.js
                       ▼
┌─────────────────────────────────────────────────┐
│                Presentation Layer                │
│  index.html (shell) + style/*.css               │
│  Dynamic DOM via view engine                    │
└─────────────────────────────────────────────────┘
```

## 2. Directory Layout

```
aicraftspeopleguild.github.io/
├── index.html                      # App shell — renderer entry point
├── README.md
├── docs/
│   ├── api/
│   └── engineering/                # This documentation
│       ├── urs/
│       ├── tech-spec/
│       ├── architecture/
│       └── component-catalog/
└── guild/
    └── web/
        ├── style/                  # CSS
        │   ├── main.css
        │   └── member-profile.css
        ├── assets/                 # Static images, media
        ├── views/                  # View template JSONs
        │   ├── page-shell.view.json
        │   ├── home.view.json
        │   ├── white-paper-index.view.json
        │   ├── white-paper-article.view.json
        │   ├── member-profile.view.json
        │   └── ...
        ├── components/             # Component type definitions
        │   └── udts/
        │       ├── templates/
        │       │   ├── component.udt.json
        │       │   ├── view.udt.json
        │       │   └── page.udt.json
        │       └── instances/
        ├── white-papers/           # Paper content + pipeline
        │   ├── udts/
        │   ├── tags/
        │   ├── originals/
        │   └── ingest.py
        ├── members/                # Member profiles + photos
        │   ├── alex-bunardzic/
        │   └── ...
        ├── renderer.js             # View engine
        └── site-map.json           # Route → view mapping
```

## 3. Type System

### 3.1 UDT Pattern

Every entity follows the Ignition-style UDT pattern:

```
{
  "udtType": "<TypeName>",
  "parameters": { ... },   // Authored fields — content, config
  "tags": { ... }          // Derived fields — ids, paths, hashes
}
```

**Parameters** are what a human or pipeline writes.
**Tags** are what the system computes.

### 3.2 Entity Types

| UDT Type | Purpose | Template Location |
|----------|---------|-------------------|
| `WhitePaper` | Paper metadata + body | `white-papers/udts/templates/` |
| `Tag` | Topic tag with paper index | `white-papers/udts/templates/` |
| `Component` | Reusable UI element definition | `components/udts/templates/` |
| `View` | Page-level template (component tree) | `components/udts/templates/` |
| `Page` | Route entry (binds URL to view + data) | `components/udts/templates/` |
| `Member` | Guild member profile | `members/udts/templates/` |
| `Document` | Engineering doc metadata | `docs/engineering/` |

### 3.3 Component → View → Page Hierarchy

```
Component  = atomic UI element (button, card, heading, badge)
             Has: props schema, CSS class, slot definitions

View       = component tree (a page template)
             Has: root component, children array, data bindings

Page       = route entry
             Has: URL path, view reference, data source references
```

A **Page** says "at this URL, render this View, fed with this data."
A **View** says "arrange these Components in this tree, binding these props."
A **Component** says "I render this HTML with these CSS classes when given these props."

## 4. Renderer Architecture

### 4.1 Boot Sequence

```
1. Browser loads index.html (minimal shell with <div id="app">)
2. renderer.js loads site-map.json
3. Router matches current path → Page instance
4. Page references a View + data sources
5. Renderer fetches View JSON + data JSONs
6. View tree is walked, each Component node rendered to DOM
7. CSS classes applied from style/*.css (already loaded in <head>)
```

### 4.2 Rendering Model

The renderer is a tree walker, not a virtual DOM. Each component node produces a DOM element:

```js
renderNode(node, data) → HTMLElement
  1. Look up node.type in component registry
  2. Resolve node.props against data context ({{ binding }} syntax)
  3. Create element with component's tag and CSS classes
  4. Recursively render node.children
  5. Append children to element
  6. Return element
```

### 4.3 Data Binding

Props support mustache-style bindings:

```json
{ "text": "{{ paper.title }}", "href": "{{ paper.site_href }}" }
```

The data context is built from the Page's data sources — typically a JSON file of UDT instances.

### 4.4 Fallback

For GitHub Pages with no JS, each existing HTML page remains functional. The renderer is progressive enhancement — it enriches `index.html` for SPA-style navigation but all content pages still work as standalone files.

## 5. Ingestion Pipeline

### 5.1 Current (White Papers)

The existing `ingest.py` handles white papers:
- Scans `originals/` for source files
- Parses metadata from front-matter or CSV columns
- Generates UDT instances in `udts/instances/`
- Rebuilds tag catalog in `tags/index.json`
- Updates manifest in `index.json`

### 5.2 Extended Pipeline

The same pattern extends to other entity types. Each entity directory gets its own `ingest.py` (or a shared `ingest-lib.py` with per-type config):

- `white-papers/ingest.py` — papers
- `members/ingest.py` — member profiles from CSV/JSON
- `components/ingest.py` — component definitions from view JSONs

All share: slugification, sha256 change detection, tag cataloging, idempotent manifests.

## 6. UDT Instance

```json:udt:Document
{
  "udtType": "Document",
  "parameters": {
    "title": "System Architecture — ACG Guild Site",
    "doc_number": "ACG-ARCH-001-2026",
    "doc_type": "architecture",
    "version": "1.0.0",
    "authors": ["Thomas Frumkin"],
    "status": "draft",
    "summary": "Architecture overview for the ACG Guild site covering directory layout, UDT type system, component-view-page hierarchy, renderer boot sequence, data binding, and ingestion pipeline.",
    "tags": ["architecture", "udt", "renderer", "site-map"]
  },
  "tags": {
    "id": "acg-arch-001-2026",
    "source_path": "docs/engineering/architecture/index.md",
    "schema_version": "1.0.0"
  }
}
```
