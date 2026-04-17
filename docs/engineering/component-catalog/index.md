# Component Catalog

**Document:** ACG-CC-001-2026  **Version:** 1.0.0

26 reusable UI components. Each is a parseable `json:udt:Component` instance. The ingest pipeline extracts these into `guild/web/components/udts/instances/` for use by the view renderer.

## Atomic Components

- **[GuildMark](guild-mark.md)** — The guild emblem displayed in every page header.
- **[Button](button.md)** — Primary and secondary action buttons.
- **[Badge](badge.md)** — Metadata label / topic tag pill.
- **[BackLink](back-link.md)** — Navigation link back to parent page.
- **[SectionHeading](section-heading.md)** — Section title with decorative underline.
- **[Callout](callout.md)** — Bordered note block for important information.
- **[PullQuote](pull-quote.md)** — Emphasized quote with attribution.
- **[CodeBlock](code-block.md)** — Syntax-highlighted code display.
- **[FigureBlock](figure-block.md)** — Image or media with caption.
- **[Eyebrow](eyebrow.md)** — Small uppercase label above headings.
- **[BadgeRow](badge-row.md)** — Horizontal row of badges.

## Composite Components

- **[PageHeader](page-header.md)** — Full page header with guild mark, title, subtitle, and optional back-link.
- **[IntroPanel](intro-panel.md)** — Opening text panel with left border accent.
- **[PaperCard](paper-card.md)** — White paper card for the papers index grid.
- **[MemberCard](member-card.md)** — Member profile card for the members directory.
- **[EntryCard](entry-card.md)** — Generic card for lists (Hall of Fame, Hall of Shame).
- **[ArticleNav](article-nav.md)** — In-page section navigation for white papers.
- **[ArticleSection](article-section.md)** — Content section within a white paper.
- **[ClosingStatement](closing-statement.md)** — Dark-background closing block for white papers.
- **[CTASection](cta-section.md)** — Call-to-action section with rotating gradient background.
- **[PageFooter](page-footer.md)** — Standard site footer with GitHub link.
- **[FutureSlot](future-slot.md)** — Dashed placeholder for upcoming content.

## Layout Components

- **[CardGrid](card-grid.md)** — Responsive grid container for cards.
- **[RawHTML](raw-html.md)** — Emits pre-rendered HTML content verbatim. Used as a bridge component while
page bodies are still aut.
- **[StaticHTMLFrame](static-html-frame.md)** — Embeds a pre-rendered HTML page as an iframe. Fallback for routes that have
not yet been decomposed.

## Page-Level Components

- **[PageShell](page-shell.md)** — The outermost page wrapper that every view uses.


## UDT Instance

```json:udt:Document
{
  "udtType": "Document",
  "parameters": {
    "title": "Component Catalog \u2014 ACG Guild Site",
    "doc_number": "ACG-CC-001-2026",
    "doc_type": "tech-spec",
    "version": "1.0.0",
    "authors": [
      "Thomas Frumkin"
    ],
    "status": "draft",
    "summary": "TOC over 26 per-component docs. Each component lives in its own file under 250 tokens.",
    "tags": [
      "components",
      "catalog",
      "udt",
      "ui"
    ]
  },
  "tags": {
    "id": "acg-cc-001-2026",
    "source_path": "docs/engineering/component-catalog/index.md",
    "schema_version": "1.0.0"
  }
}
```
