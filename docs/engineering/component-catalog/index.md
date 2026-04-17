# Component Catalog — ACG Guild Site

**Document:** ACG-CC-001-2026
**Version:** 1.0.0

Each component below is a parseable `json:udt:Component` instance. Tooling can extract these blocks to seed `guild/web/components/udts/instances/`.

---

## Atomic Components

### GuildMark

The guild emblem displayed in every page header.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "GuildMark",
    "tag": "div",
    "cssClass": "guild-mark",
    "description": "Guild emblem branding element with hammers and ACG text.",
    "category": "atomic",
    "props": {},
    "slots": [],
    "template": "<div class=\"guild-mark\"><div class=\"emblem\">⚒ ACG ⚒</div></div>"
  },
  "tags": {
    "id": "guild-mark",
    "file_path": "guild/web/components/guild-mark.json",
    "dependencies": [],
    "used_by_views": ["page-shell"],
    "schema_version": "1.0.0"
  }
}
```

### Button

Primary and secondary action buttons.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "Button",
    "tag": "a",
    "cssClass": "btn",
    "description": "Action button with primary/secondary variants.",
    "category": "atomic",
    "props": {
      "text":    { "type": "String",  "required": true },
      "href":    { "type": "URL",     "required": true },
      "variant": { "type": "Enum",    "required": false, "default": "primary", "options": ["primary", "secondary"] }
    },
    "slots": [],
    "template": "<a href=\"{{ href }}\" class=\"btn btn-{{ variant }}\">{{ text }}</a>"
  },
  "tags": {
    "id": "button",
    "file_path": "guild/web/components/button.json",
    "dependencies": [],
    "used_by_views": ["page-shell", "white-paper-index", "member-profile", "home"],
    "schema_version": "1.0.0"
  }
}
```

### Badge

Metadata label / topic tag pill.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "Badge",
    "tag": "span",
    "cssClass": "badge",
    "description": "Small label for metadata, tags, or status indicators.",
    "category": "atomic",
    "props": {
      "text": { "type": "String", "required": true }
    },
    "slots": [],
    "template": "<span class=\"badge\">{{ text }}</span>"
  },
  "tags": {
    "id": "badge",
    "file_path": "guild/web/components/badge.json",
    "dependencies": [],
    "used_by_views": ["paper-card", "member-card", "white-paper-article"],
    "schema_version": "1.0.0"
  }
}
```

### BackLink

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

### SectionHeading

Section title with decorative underline.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "SectionHeading",
    "tag": "div",
    "cssClass": "section-heading",
    "description": "Section title with bronze underline and optional subtitle.",
    "category": "atomic",
    "props": {
      "title":    { "type": "String", "required": true },
      "subtitle": { "type": "String", "required": false }
    },
    "slots": [],
    "template": "<div class=\"section-heading\"><h2>{{ title }}</h2><p>{{ subtitle }}</p></div>"
  },
  "tags": {
    "id": "section-heading",
    "file_path": "guild/web/components/section-heading.json",
    "dependencies": [],
    "used_by_views": ["white-paper-index", "members-index", "home"],
    "schema_version": "1.0.0"
  }
}
```

### Callout

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

### PullQuote

Emphasized quote with attribution.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "PullQuote",
    "tag": "div",
    "cssClass": "pull-quote",
    "description": "Highlighted quote block with rust left border and serif font.",
    "category": "atomic",
    "props": {
      "text":        { "type": "String", "required": true },
      "attribution": { "type": "String", "required": false }
    },
    "slots": [],
    "template": "<div class=\"pull-quote\">\"{{ text }}\" — {{ attribution }}</div>"
  },
  "tags": {
    "id": "pull-quote",
    "file_path": "guild/web/components/pull-quote.json",
    "dependencies": [],
    "used_by_views": ["white-paper-article", "mob-programming"],
    "schema_version": "1.0.0"
  }
}
```

### CodeBlock

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

### FigureBlock

Image or media with caption.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "FigureBlock",
    "tag": "figure",
    "cssClass": "figure-block",
    "description": "Image or media figure with optional caption, parchment background.",
    "category": "atomic",
    "props": {
      "src":     { "type": "URL",    "required": true },
      "alt":     { "type": "String", "required": true },
      "caption": { "type": "String", "required": false },
      "type":    { "type": "Enum",   "required": false, "default": "image", "options": ["image", "video"] }
    },
    "slots": [],
    "template": "<figure class=\"figure-block\"><img src=\"{{ src }}\" alt=\"{{ alt }}\"><figcaption>{{ caption }}</figcaption></figure>"
  },
  "tags": {
    "id": "figure-block",
    "file_path": "guild/web/components/figure-block.json",
    "dependencies": [],
    "used_by_views": ["white-paper-article"],
    "schema_version": "1.0.0"
  }
}
```

### Eyebrow

Small uppercase label above headings.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "Eyebrow",
    "tag": "p",
    "cssClass": "eyebrow",
    "description": "Small uppercase label used above page titles for context.",
    "category": "atomic",
    "props": {
      "text": { "type": "String", "required": true }
    },
    "slots": [],
    "template": "<p class=\"eyebrow\">{{ text }}</p>"
  },
  "tags": {
    "id": "eyebrow",
    "file_path": "guild/web/components/eyebrow.json",
    "dependencies": [],
    "used_by_views": ["page-header", "member-profile", "white-paper-article"],
    "schema_version": "1.0.0"
  }
}
```

### BadgeRow

Horizontal row of badges.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "BadgeRow",
    "tag": "div",
    "cssClass": "badge-row",
    "description": "Flex row of Badge components for tags or metadata.",
    "category": "atomic",
    "props": {
      "items": { "type": "StringArray", "required": true }
    },
    "slots": [],
    "template": "<div class=\"badge-row\">{{ #items }}<span class=\"badge\">{{ . }}</span>{{ /items }}</div>"
  },
  "tags": {
    "id": "badge-row",
    "file_path": "guild/web/components/badge-row.json",
    "dependencies": ["badge"],
    "used_by_views": ["flywheel", "mob-programming"],
    "schema_version": "1.0.0"
  }
}
```

---

## Composite Components

### PageHeader

Full page header with guild mark, title, subtitle, and optional back-link.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "PageHeader",
    "tag": "header",
    "cssClass": "",
    "description": "Full page header assembling GuildMark, title, subtitle, eyebrow, article-meta, and BackLink.",
    "category": "composite",
    "props": {
      "title":       { "type": "String",      "required": true },
      "subtitle":    { "type": "String",      "required": false },
      "eyebrow":     { "type": "String",      "required": false },
      "backHref":    { "type": "URL",         "required": false },
      "backLabel":   { "type": "String",      "required": false },
      "meta":        { "type": "StringArray", "required": false, "description": "Article metadata badges" }
    },
    "slots": [],
    "template": "<header><div class=\"guild-mark\"><div class=\"emblem\">⚒ ACG ⚒</div></div>{{ #eyebrow }}<p class=\"eyebrow\">{{ eyebrow }}</p>{{ /eyebrow }}<h1>{{ title }}</h1>{{ #subtitle }}<p class=\"subtitle\">{{ subtitle }}</p>{{ /subtitle }}{{ #meta }}<div class=\"article-meta\">{{ #meta }}<span>{{ . }}</span>{{ /meta }}</div>{{ /meta }}{{ #backHref }}<div class=\"back-link\"><a href=\"{{ backHref }}\">← {{ backLabel }}</a></div>{{ /backHref }}</header>"
  },
  "tags": {
    "id": "page-header",
    "file_path": "guild/web/components/page-header.json",
    "dependencies": ["guild-mark", "eyebrow", "back-link"],
    "used_by_views": ["page-shell"],
    "schema_version": "1.0.0"
  }
}
```

### IntroPanel

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

### PaperCard

White paper card for the papers index grid.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "PaperCard",
    "tag": "article",
    "cssClass": "paper-card",
    "description": "Card displaying a white paper summary with metadata, title, description, and read action.",
    "category": "composite",
    "props": {
      "title":     { "type": "String",      "required": true },
      "authors":   { "type": "StringArray", "required": false },
      "date":      { "type": "String",      "required": false },
      "docNumber": { "type": "String",      "required": false },
      "summary":   { "type": "String",      "required": false },
      "href":      { "type": "URL",         "required": true },
      "status":    { "type": "String",      "required": false },
      "tags":      { "type": "StringArray", "required": false },
      "paperType": { "type": "String",      "required": false, "description": "knowledge-paper | position-paper | experimental-paper | research-note" }
    },
    "slots": [],
    "template": "<article class=\"paper-card {{ paperType }}\">{{ #paperType }}<div class=\"paper-type\">{{ paperType }}</div>{{ /paperType }}<div class=\"paper-meta\">{{ #authors }}<span>{{ . }}</span>{{ /authors }}{{ #date }}<span>{{ date }}</span>{{ /date }}{{ #docNumber }}<span>{{ docNumber }}</span>{{ /docNumber }}</div><h3>{{ title }}</h3><p>{{ summary }}</p><div class=\"paper-actions\"><a href=\"{{ href }}\" class=\"btn btn-primary\">Read White Paper</a></div></article>"
  },
  "tags": {
    "id": "paper-card",
    "file_path": "guild/web/components/paper-card.json",
    "dependencies": ["button", "badge"],
    "used_by_views": ["white-paper-index"],
    "schema_version": "1.0.0"
  }
}
```

### MemberCard

Member profile card for the members directory.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "MemberCard",
    "tag": "article",
    "cssClass": "member-card",
    "description": "Full member card with photo, bio, tags, and profile link. Used on the members index page.",
    "category": "composite",
    "props": {
      "name":          { "type": "String",      "required": true },
      "role":          { "type": "String",      "required": false },
      "title":         { "type": "String",      "required": false },
      "bio":           { "type": "String",      "required": false },
      "summary":       { "type": "String",      "required": false },
      "avatarSrc":     { "type": "URL",         "required": false },
      "avatarAlt":     { "type": "String",      "required": false },
      "profileHref":   { "type": "URL",         "required": false },
      "expertiseTags": { "type": "StringArray", "required": false }
    },
    "slots": [],
    "template": "<article class=\"member-card\"><div class=\"member-meta\">{{ #role }}<span>{{ role }}</span>{{ /role }}{{ #title }}<span>{{ title }}</span>{{ /title }}</div><h3><a href=\"{{ profileHref }}\">{{ name }}</a></h3><div class=\"profile-layout\">{{ #avatarSrc }}<div class=\"member-photo\"><img src=\"{{ avatarSrc }}\" alt=\"{{ avatarAlt }}\"></div>{{ /avatarSrc }}<div class=\"member-body\">{{ #summary }}<p class=\"member-summary\">{{ summary }}</p>{{ /summary }}<div class=\"member-tags\">{{ #expertiseTags }}<span>{{ . }}</span>{{ /expertiseTags }}</div><p>{{ bio }}</p><div class=\"member-actions\"><a href=\"{{ profileHref }}\" class=\"btn btn-primary\">Read Full Profile</a></div></div></div></article>"
  },
  "tags": {
    "id": "member-card",
    "file_path": "guild/web/components/member-card.json",
    "dependencies": ["button", "badge"],
    "used_by_views": ["members-index"],
    "schema_version": "1.0.0"
  }
}
```

### EntryCard

Generic card for lists (Hall of Fame, Hall of Shame).

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "EntryCard",
    "tag": "article",
    "cssClass": "entry-card",
    "description": "Generic list entry card with metadata, title, and description.",
    "category": "composite",
    "props": {
      "title":    { "type": "String",      "required": true },
      "content":  { "type": "String",      "required": false },
      "meta":     { "type": "StringArray", "required": false }
    },
    "slots": [],
    "template": "<article class=\"entry-card\"><div class=\"entry-meta\">{{ #meta }}<span>{{ . }}</span>{{ /meta }}</div><h3>{{ title }}</h3><p>{{ content }}</p></article>"
  },
  "tags": {
    "id": "entry-card",
    "file_path": "guild/web/components/entry-card.json",
    "dependencies": [],
    "used_by_views": ["hall-of-fame", "hall-of-shame"],
    "schema_version": "1.0.0"
  }
}
```

### CardGrid

Responsive grid container for cards.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "CardGrid",
    "tag": "section",
    "cssClass": "",
    "description": "Responsive auto-fit grid wrapper with section heading. Wraps any card type.",
    "category": "layout",
    "props": {
      "heading":    { "type": "String", "required": false },
      "subheading": { "type": "String", "required": false },
      "gridClass":  { "type": "String", "required": false, "default": "papers-grid" },
      "shellClass": { "type": "String", "required": false, "default": "papers-shell" },
      "minWidth":   { "type": "String", "required": false, "default": "300px" }
    },
    "slots": ["default"],
    "template": "<section class=\"{{ shellClass }}\">{{ #heading }}<div class=\"section-heading\"><h2>{{ heading }}</h2>{{ #subheading }}<p>{{ subheading }}</p>{{ /subheading }}</div>{{ /heading }}<div class=\"{{ gridClass }}\">{{ slot:default }}</div></section>"
  },
  "tags": {
    "id": "card-grid",
    "file_path": "guild/web/components/card-grid.json",
    "dependencies": ["section-heading"],
    "used_by_views": ["white-paper-index", "members-index", "hall-of-fame", "hall-of-shame"],
    "schema_version": "1.0.0"
  }
}
```

### ArticleNav

In-page section navigation for white papers.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "ArticleNav",
    "tag": "nav",
    "cssClass": "article-nav",
    "description": "Horizontal navigation bar linking to article sections within a white paper.",
    "category": "composite",
    "props": {
      "sections": { "type": "JSON", "required": true, "description": "Array of { id, label } objects" }
    },
    "slots": [],
    "template": "<nav class=\"article-nav\" aria-label=\"Article sections\">{{ #sections }}<a href=\"#{{ id }}\">{{ label }}</a>{{ /sections }}</nav>"
  },
  "tags": {
    "id": "article-nav",
    "file_path": "guild/web/components/article-nav.json",
    "dependencies": [],
    "used_by_views": ["white-paper-article"],
    "schema_version": "1.0.0"
  }
}
```

### ArticleSection

Content section within a white paper.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "ArticleSection",
    "tag": "section",
    "cssClass": "section",
    "description": "Content section with heading, body text, and optional sub-components (callouts, figures, code blocks).",
    "category": "composite",
    "props": {
      "id":    { "type": "String", "required": true },
      "title": { "type": "String", "required": true }
    },
    "slots": ["default"],
    "template": "<section id=\"{{ id }}\" class=\"section\"><h2>{{ title }}</h2>{{ slot:default }}</section>"
  },
  "tags": {
    "id": "article-section",
    "file_path": "guild/web/components/article-section.json",
    "dependencies": [],
    "used_by_views": ["white-paper-article"],
    "schema_version": "1.0.0"
  }
}
```

### ClosingStatement

Dark-background closing block for white papers.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "ClosingStatement",
    "tag": "div",
    "cssClass": "closing-statement",
    "description": "Dark gradient closing block at the end of white papers with light text.",
    "category": "composite",
    "props": {
      "content":   { "type": "String", "required": true },
      "paperMark": { "type": "String", "required": false, "description": "Centered mark text below closing" }
    },
    "slots": [],
    "template": "<div class=\"closing-statement\"><p>{{ content }}</p></div>{{ #paperMark }}<p class=\"paper-mark\">{{ paperMark }}</p>{{ /paperMark }}"
  },
  "tags": {
    "id": "closing-statement",
    "file_path": "guild/web/components/closing-statement.json",
    "dependencies": [],
    "used_by_views": ["white-paper-article"],
    "schema_version": "1.0.0"
  }
}
```

### CTASection

Call-to-action section with rotating gradient background.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "CTASection",
    "tag": "section",
    "cssClass": "cta-section",
    "description": "Call-to-action section with rotating gradient background and primary/secondary buttons.",
    "category": "composite",
    "props": {
      "heading":       { "type": "String", "required": true },
      "description":   { "type": "String", "required": false },
      "primaryText":   { "type": "String", "required": false },
      "primaryHref":   { "type": "URL",    "required": false },
      "secondaryText": { "type": "String", "required": false },
      "secondaryHref": { "type": "URL",    "required": false }
    },
    "slots": [],
    "template": "<section class=\"cta-section\"><h2>{{ heading }}</h2>{{ #description }}<p>{{ description }}</p>{{ /description }}<div class=\"cta-actions\">{{ #primaryHref }}<a href=\"{{ primaryHref }}\" class=\"btn btn-primary\">{{ primaryText }}</a>{{ /primaryHref }}{{ #secondaryHref }}<a href=\"{{ secondaryHref }}\" class=\"btn btn-secondary\">{{ secondaryText }}</a>{{ /secondaryHref }}</div></section>"
  },
  "tags": {
    "id": "cta-section",
    "file_path": "guild/web/components/cta-section.json",
    "dependencies": ["button"],
    "used_by_views": ["page-shell", "home", "white-paper-index", "members-index"],
    "schema_version": "1.0.0"
  }
}
```

### PageFooter

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

### FutureSlot

Dashed placeholder for upcoming content.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "FutureSlot",
    "tag": "div",
    "cssClass": "future-slot",
    "description": "Dashed-border placeholder card for content that is planned but not yet published.",
    "category": "composite",
    "props": {
      "title":   { "type": "String",  "required": true },
      "content": { "type": "String",  "required": false },
      "href":    { "type": "URL",     "required": false },
      "linked":  { "type": "Boolean", "required": false, "default": false }
    },
    "slots": [],
    "template": "<div class=\"future-slot {{ #linked }}future-slot-link{{ /linked }}\"><h3>{{ title }}</h3><p>{{ content }}</p></div>"
  },
  "tags": {
    "id": "future-slot",
    "file_path": "guild/web/components/future-slot.json",
    "dependencies": [],
    "used_by_views": ["white-paper-index", "members-index", "hall-of-fame"],
    "schema_version": "1.0.0"
  }
}
```

---

## Page-Level Components

### PageShell

The outermost page wrapper that every view uses.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "PageShell",
    "tag": "fragment",
    "cssClass": "",
    "description": "Logical page body wrapper. Emits <header> with guild-mark/title/subtitle/back-link, then <main class=\"container\">children</main>, then <footer>. The build.js wraps this with <!DOCTYPE html><html><head>...</head><body>[shell]</body></html>. The 'fragment' tag is a sentinel telling the renderer not to wrap output in an element.",
    "category": "page-level",
    "props": {
      "title":       { "type": "String",      "required": true },
      "bodyClass":   { "type": "String",      "required": false },
      "stylesheets": { "type": "StringArray", "required": false },
      "subtitle":    { "type": "String",      "required": false },
      "eyebrow":     { "type": "String",      "required": false },
      "backHref":    { "type": "URL",         "required": false },
      "backLabel":   { "type": "String",      "required": false },
      "meta":        { "type": "StringArray", "required": false }
    },
    "slots": ["default"],
    "template": "<header><div class=\"guild-mark\"><div class=\"emblem\">⚒ ACG ⚒</div></div>{{ #eyebrow }}<p class=\"eyebrow\">{{ eyebrow }}</p>{{ /eyebrow }}<h1>{{ title }}</h1>{{ #subtitle }}<p class=\"subtitle\">{{ subtitle }}</p>{{ /subtitle }}{{ #backHref }}<div class=\"back-link\"><a href=\"{{ backHref }}\">← {{ backLabel }}</a></div>{{ /backHref }}</header>\n<main class=\"container\">{{ slot:default }}</main>\n<footer><p>© 2026 AI Craftspeople Guild. Built by practitioners, not evangelists.</p><p><a href=\"https://github.com/aicraftspeopleguild\">GitHub</a></p></footer>"
  },
  "tags": {
    "id": "page-shell",
    "file_path": "guild/web/components/page-shell.json",
    "dependencies": ["page-header", "page-footer", "guild-mark"],
    "used_by_views": ["home", "white-paper-index", "white-paper-article", "members-index", "member-profile", "charter", "flywheel", "mob-programming", "hall-of-fame", "hall-of-shame"],
    "schema_version": "1.0.0"
  }
}
```

### RawHTML

Emits pre-rendered HTML content verbatim. Used as a bridge component while
page bodies are still authored as HTML strings (in views/data/*.data.json)
rather than fully decomposed component trees.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "RawHTML",
    "tag": "fragment",
    "cssClass": "",
    "description": "Emits a pre-rendered HTML string verbatim using the {{{ html }}} triple-brace (unescaped) syntax. Content lives in data files, not in HTML files.",
    "category": "layout",
    "props": {
      "html": { "type": "String", "required": true }
    },
    "slots": [],
    "template": "{{{ html }}}"
  },
  "tags": {
    "id": "raw-html",
    "file_path": "guild/web/components/raw-html.json",
    "dependencies": [],
    "used_by_views": ["charter", "flywheel", "mob-programming", "hall-of-fame", "hall-of-shame", "hushbell", "showcases"],
    "schema_version": "1.0.0"
  }
}
```

### StaticHTMLFrame

Embeds a pre-rendered HTML page as an iframe. Fallback for routes that have
not yet been decomposed.

```json:udt:Component
{
  "udtType": "Component",
  "parameters": {
    "name": "StaticHTMLFrame",
    "tag": "iframe",
    "cssClass": "static-html-frame",
    "description": "Embeds a pre-rendered HTML page as an iframe.",
    "category": "layout",
    "props": {
      "src":   { "type": "URL",    "required": true },
      "title": { "type": "String", "required": false }
    },
    "slots": [],
    "template": ""
  },
  "tags": {
    "id": "static-html-frame",
    "file_path": "guild/web/components/static-html-frame.json",
    "dependencies": [],
    "used_by_views": ["static-page"],
    "schema_version": "1.0.0"
  }
}
```

---

## UDT Instance

```json:udt:Document
{
  "udtType": "Document",
  "parameters": {
    "title": "Component Catalog — ACG Guild Site",
    "doc_number": "ACG-CC-001-2026",
    "doc_type": "tech-spec",
    "version": "1.0.0",
    "authors": ["Thomas Frumkin"],
    "status": "draft",
    "summary": "Full catalog of 22 reusable UI components extracted from the ACG site, each defined as a parseable Component UDT instance with typed props, slots, CSS classes, and HTML templates.",
    "tags": ["components", "catalog", "udt", "ui"]
  },
  "tags": {
    "id": "acg-cc-001-2026",
    "source_path": "docs/engineering/component-catalog/index.md",
    "schema_version": "1.0.0"
  }
}
```
