# Technical Specification — ACG Guild Site

**Document:** ACG-TS-001-2026
**Version:** 1.0.0
**Status:** Draft

---

## 1. Scope

This spec covers the implementation details for the ACG component system, view renderer, and site map. It bridges the URS requirements to concrete file formats, APIs, and rendering behavior.

## 2. Component System

### 2.1 Component Definition

A Component is a reusable UI building block. Each is defined by a UDT instance that declares its HTML tag, CSS classes, prop schema, and child slot rules.

**Props** are typed inputs the component accepts.
**Slots** are named positions where child components can be inserted.
**CSS classes** are applied to the root element.

### 2.2 Prop Types

| Type | Description | Example |
|------|-------------|---------|
| `String` | Text value | `"AI Harness"` |
| `StringArray` | List of strings | `["TDD", "ethics"]` |
| `URL` | Href/src value | `"white-papers/ai-harness.html"` |
| `Boolean` | Toggle | `true` |
| `Enum` | Constrained string | `"primary"` or `"secondary"` |
| `ComponentTree` | Nested children | `[{ "type": "Badge", ... }]` |

### 2.3 Component Registry

Components are registered by name. The renderer looks up each `type` string in the registry to find the component definition:

```json
{
  "GuildMark":     "components/guild-mark.json",
  "PageHeader":    "components/page-header.json",
  "BackLink":      "components/back-link.json",
  "SectionHeading":"components/section-heading.json",
  "Button":        "components/button.json",
  "Badge":         "components/badge.json",
  "PaperCard":     "components/paper-card.json",
  "MemberCard":    "components/member-card.json",
  "EntryCard":     "components/entry-card.json",
  "CardGrid":      "components/card-grid.json",
  "IntroPanel":    "components/intro-panel.json",
  "ArticleNav":    "components/article-nav.json",
  "ArticleSection":"components/article-section.json",
  "ClosingStatement":"components/closing-statement.json",
  "CTASection":    "components/cta-section.json",
  "PageFooter":    "components/page-footer.json",
  "Callout":       "components/callout.json",
  "FigureBlock":   "components/figure-block.json",
  "CodeBlock":     "components/code-block.json",
  "PullQuote":     "components/pull-quote.json"
}
```

## 3. View Templates

### 3.1 View Structure

A View is a tree of component instances with data bindings:

```json
{
  "udtType": "View",
  "parameters": {
    "name": "white-paper-index",
    "description": "White papers listing page",
    "root": {
      "type": "PageShell",
      "props": {
        "title": "White Papers",
        "subtitle": "{{ page.subtitle }}",
        "bodyClass": "page-white-papers",
        "stylesheets": ["style/main.css"]
      },
      "children": [
        {
          "type": "IntroPanel",
          "props": { "content": "{{ page.intro }}" }
        },
        {
          "type": "CardGrid",
          "props": {
            "heading": "Available Papers",
            "subheading": "{{ page.grid_subheading }}",
            "gridClass": "papers-grid",
            "minWidth": "300px"
          },
          "repeat": {
            "source": "papers",
            "as": "paper",
            "template": {
              "type": "PaperCard",
              "props": {
                "title": "{{ paper.title }}",
                "authors": "{{ paper.authors }}",
                "date": "{{ paper.publication_date }}",
                "docNumber": "{{ paper.doc_number }}",
                "summary": "{{ paper.summary }}",
                "href": "{{ paper.site_href }}",
                "status": "{{ paper.status }}",
                "tags": "{{ paper.tags }}"
              }
            }
          }
        }
      ]
    }
  }
}
```

### 3.2 Repeat Blocks

The `repeat` key iterates over a data array. For each item, a new component is rendered with the item bound into scope:

```json
{
  "repeat": {
    "source": "papers",        // key in data context
    "as": "paper",             // loop variable name
    "template": { ... }        // component to render per item
  }
}
```

### 3.3 Conditionals

The `when` key controls conditional rendering:

```json
{
  "type": "Badge",
  "when": "{{ paper.doc_number }}",
  "props": { "text": "{{ paper.doc_number }}" }
}
```

Falsy values (`""`, `null`, `false`, `0`, empty array) suppress the node.

## 4. Page Definitions & Site Map

### 4.1 Page UDT

A Page binds a URL route to a View template and data sources:

```json
{
  "udtType": "Page",
  "parameters": {
    "title": "White Papers",
    "slug": "white-papers",
    "route": "/guild/web/white-papers.html",
    "view": "views/white-paper-index.view.json",
    "data": {
      "papers": "white-papers/index.json",
      "page": "views/data/white-paper-index.data.json"
    },
    "stylesheets": ["style/main.css"],
    "section": "resources",
    "parent_slug": "home"
  }
}
```

### 4.2 Site Map

`site-map.json` is the master route table. The renderer consults it on load:

```json
{
  "version": "1.0.0",
  "base": "/guild/web/",
  "routes": [
    {
      "path": "/",
      "page": "pages/home.page.json"
    },
    {
      "path": "/white-papers",
      "page": "pages/white-paper-index.page.json"
    },
    {
      "path": "/white-papers/:slug",
      "page": "pages/white-paper-article.page.json",
      "dynamic": true
    },
    {
      "path": "/members",
      "page": "pages/members-index.page.json"
    },
    {
      "path": "/members/:slug",
      "page": "pages/member-profile.page.json",
      "dynamic": true
    }
  ]
}
```

Dynamic routes use `:slug` parameters resolved against UDT instance IDs.

## 5. Renderer API

### 5.1 Public Interface

```js
// Boot the renderer
ACGRenderer.init({
  siteMap:    'guild/web/site-map.json',
  components: 'guild/web/components/registry.json',
  mountPoint: '#app'
});

// Navigate programmatically
ACGRenderer.navigate('/white-papers/ai-harness');

// Re-render current view with new data
ACGRenderer.refresh();
```

### 5.2 Component Lifecycle

```
1. resolve(props, dataContext)  → bound props
2. createElement(tag, classes)  → DOM element
3. renderSlots(children, el)    → append child elements
4. mount(el, parent)            → insert into DOM
```

No virtual DOM, no diffing. Full re-render on navigation. This keeps the renderer simple and appropriate for a static content site.

### 5.3 Progressive Enhancement

The renderer checks for `#app` mount point. If missing (standalone HTML page), it does nothing. This means:

- All existing HTML pages continue to work without JS
- `index.html` gets SPA navigation when JS is available
- Search engines see full HTML content on direct page loads

## 6. CSS Architecture

### 6.1 Design Tokens

All visual constants are CSS custom properties on `:root`:

| Token | Value | Usage |
|-------|-------|-------|
| `--color-parchment` | `#F5F1E8` | Page background |
| `--color-ink` | `#1A1614` | Primary text |
| `--color-rust` | `#C84B31` | Primary CTA, emphasis |
| `--color-bronze` | `#A67C52` | Secondary accent |
| `--color-graphite` | `#2D3436` | Body copy |
| `--color-highlight` | `#FFF4E0` | Callout backgrounds |
| `--color-shadow` | `rgba(26,22,20,0.08)` | Box shadows |
| `--color-accent` | varies per page | Page-specific accent |

### 6.2 Class Naming

Classes follow a flat BEM-lite convention:

- Block: `.paper-card`, `.member-card`, `.intro-panel`
- Element: `.paper-meta`, `.paper-actions`, `.member-photo`
- Modifier: `.btn-primary`, `.btn-secondary`, `.knowledge-paper`

### 6.3 Typography Scale

| Element | Font | Size | Weight |
|---------|------|------|--------|
| h1 | Playfair Display | clamp(2.5rem, 7vw, 5rem) | 900 |
| h2 | Playfair Display | clamp(2rem, 4vw, 3rem) | 700 |
| h3 | Playfair Display | 1.45rem | 700 |
| body | Work Sans | 1.06rem | 400 |
| code | Courier Prime | 0.95rem | 400 |
| .eyebrow | Work Sans | 0.9rem | 600, uppercase |

## 7. UDT Instance

```json:udt:Document
{
  "udtType": "Document",
  "parameters": {
    "title": "Technical Specification — ACG Guild Site",
    "doc_number": "ACG-TS-001-2026",
    "doc_type": "tech-spec",
    "version": "1.0.0",
    "authors": ["Thomas Frumkin"],
    "status": "draft",
    "summary": "Implementation specification covering the component system, view templates, page definitions, site map, renderer API, and CSS architecture for the ACG Guild site.",
    "tags": ["tech-spec", "components", "renderer", "css", "views"]
  },
  "tags": {
    "id": "acg-ts-001-2026",
    "source_path": "docs/engineering/tech-spec/index.md",
    "schema_version": "1.0.0"
  }
}
```
