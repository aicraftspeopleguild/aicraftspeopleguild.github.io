---
acg-paper:
  id: ACG-STD-AUTOPARSE-2026
  type: standard
  title: "Paper Auto-Index Standard"
  author: "AI Craftspeople Guild"
  date: 2026-04-17
  status: published
  tags: [automation, github-actions, indexing, white-papers, standards]
  abstract: >
    Defines the frontmatter format, parser rules, and GitHub Action pipeline
    for automatically indexing Guild publications when submitted via Pull Request.
    This document uses its own frontmatter format, making it self-validating.
---

# Paper Auto-Index Standard

*AI Craftspeople Guild · April 2026*

This document defines how Guild publications are automatically parsed, classified,
and listed on the white papers page when submitted via Pull Request.

This document uses its own format. If the parser can read this file,
the standard is working.

---

## How It Works

An author writes a paper. They add a small metadata block at the top.
They open a Pull Request. A GitHub Action reads the metadata, assigns an ID
if needed, extracts keywords if missing, rebuilds the index page, and posts
a summary on the PR. The author never touches the index page. The action
is the librarian.

---

## Part 1 — The Frontmatter Block

Every publication must include a metadata block. The format depends on
the file type, but the fields are always the same.

### For HTML files

Place inside an HTML comment in the first 50 lines:

```html
<!--
acg-paper:
  id: ACG-WP-005-2026
  type: white-paper
  title: "My Paper Title"
  author: "Jane Smith (Affiliation)"
  date: 2026-04-17
  status: published
  tags: [ai-safety, governance]
  abstract: "A one-paragraph description for the index card."
-->
```

### For Markdown files

Place in standard YAML frontmatter:

```markdown
---
acg-paper:
  id: ACG-WP-005-2026
  type: white-paper
  title: "My Paper Title"
  author: "Jane Smith"
  date: 2026-04-17
  status: published
  tags: [ai-safety, governance]
  abstract: "A one-paragraph description for the index card."
---
```

### For PDF files

Place a companion sidecar file with the same name:

```
my-paper.pdf
my-paper.meta.yml
```

The sidecar contains the same fields:

```yaml
acg-paper:
  id: ACG-WP-005-2026
  type: white-paper
  title: "My Paper Title"
  author: "Jane Smith"
  date: 2026-04-17
  status: published
  tags: [ai-safety, governance]
  abstract: "A one-paragraph description."
  file: my-paper.pdf
```

---

## Part 2 — Field Definitions

### Required Fields

| Field      | Type     | If Missing                  | Purpose                                    |
|------------|----------|-----------------------------|--------------------------------------------|
| `title`    | string   | reject the PR               | The name of the paper                      |
| `author`   | string   | reject the PR               | Who wrote it                               |
| `type`     | enum     | reject the PR               | What kind of publication it is             |
| `abstract` | string   | reject the PR               | The description shown on the index card    |

### Auto-Filled Fields

| Field      | Type     | If Missing                  | Purpose                                    |
|------------|----------|-----------------------------|--------------------------------------------|
| `id`       | string   | auto-increment from highest | Unique identifier, never reassigned        |
| `date`     | date     | set to today                | Publication date in ISO 8601               |
| `status`   | enum     | default to `draft`          | Where the paper is in its lifecycle        |
| `tags`     | string[] | auto-extract from text      | Keywords for search and filtering          |
| `slug`     | string   | derive from filename        | URL-safe identifier                        |

### Enum Values

**type** — what kind of publication:

| Value              | Label on Page              | Description                              |
|--------------------|----------------------------|------------------------------------------|
| `white-paper`      | White Paper                | Core Guild technical publication         |
| `position-paper`   | Position Paper             | Guild stance on a topic                  |
| `experimental`     | Experimental               | Speculative, explicitly flagged          |
| `research-note`    | Research Note              | Short supporting essay                   |
| `knowledge`        | Knowledge About Knowledge  | Systems thinking, epistemics, meta       |
| `standard`         | Standard                   | Guild process or format definition       |

**status** — lifecycle stage:

| Value       | Meaning                                          |
|-------------|--------------------------------------------------|
| `draft`     | Work in progress, not ready for review           |
| `review`    | Submitted for peer review                        |
| `published` | Approved and live on the site                    |
| `archived`  | Superseded or withdrawn, kept for reference      |

---

## Part 3 — Tag Vocabulary

Tags are lowercase kebab-case. The parser recognizes these known tags
and will auto-extract them from the title and abstract when the author
omits the `tags` field.

**Core topics:** ai-safety, governance, testing, ethics, architecture,
automation, calibration, peer-review, culture, epistemics, falsification,
consciousness, harness, federation, healthcare, standards.

**Technical topics:** blockchain, konomi, isa-88, isa-95, packml, scada,
opc-ua, guild-chain, guild-ops, webrtc, p2p, github-actions, ci-cd.

**Meta topics:** knowledge-about-knowledge, systems-thinking,
cognitive-apprenticeship, triad-engine, toast, occam.

Authors may add tags not in this list. New tags are accepted without
validation. The vocabulary grows organically.

---

## Part 4 — The Parser

**Step 1 — Scan.**

| File Pattern       | Where to Look                               |
|--------------------|---------------------------------------------|
| `*.html`           | HTML comment `<!--acg-paper: ... -->`       |
| `*.md`             | YAML frontmatter `---acg-paper: ... ---`    |
| `*.meta.yml`       | Entire file is the metadata (for PDFs)      |

**Step 2 — Parse.** Extract YAML, validate required fields. If `title`,
`author`, `type`, or `abstract` are missing, post a warning on the PR
and skip the file.

**Step 3 — Fill.** For each missing optional field:

- `id` — scan `papers.json` for highest `ACG-WP-NNN`, increment.
- `date` — today.
- `status` — `draft`.
- `tags` — scan title + abstract against vocabulary.
- `slug` — strip extension from filename.

**Step 4 — Sort.** Group by type (in enum order), then newest first by
date, then alphabetical by title.

**Step 5 — Generate.** Rebuild `papers.json` + `white-papers.html`.

**Step 6 — Validate.** Every URL resolves. No duplicate IDs. All dates
valid ISO 8601. All enum values valid.

**Step 7 — Commit.** Add generated files to the PR branch.

**Step 8 — Comment.** Post a summary on the PR.

---

## Part 5 — The Index Card Template

```html
<article class="paper-card" data-type="{type}" data-tags="{tags joined}">
  <div class="paper-meta">
    <span class="paper-author">{author}</span>
    <span class="paper-date">{date formatted}</span>
    <span class="paper-id">{id}</span>
  </div>
  <div class="paper-type-badge">{Type Label}</div>
  <h3>{title}</h3>
  <p class="paper-abstract">{abstract}</p>
  <div class="paper-tags">
    <span class="tag">{tag}</span>
  </div>
  <a href="{slug}.html" class="paper-link">Read {Type Label} →</a>
</article>
```

If `status` is `draft` or `review`, add a status badge.

---

## Part 6 — papers.json

```json
[
  {
    "id": "ACG-WP-005-2026",
    "type": "white-paper",
    "title": "My Paper Title",
    "author": "Jane Smith",
    "date": "2026-04-17",
    "status": "published",
    "tags": ["ai-safety", "governance"],
    "abstract": "A one-paragraph description.",
    "slug": "my-paper",
    "url": "https://aicraftspeopleguild.github.io/my-paper.html"
  }
]
```

`papers.json` is the source of truth. The HTML index is generated from it.

---

## Part 7 — The GitHub Action

See `.github/workflows/paper-index.yml` and `.github/scripts/*.js`
for the full implementation.

---

## Part 8 — Author Checklist

1. Write your paper as `.html`, `.md`, or `.pdf`.
2. Add the `acg-paper:` metadata block.
3. Fill in: `title`, `author`, `type`, `abstract`.
4. Leave `id` blank — the bot assigns it.
5. Tags optional — the bot extracts.
6. Open a Pull Request.
7. The bot parses, indexes, and comments.
8. Merge to main. Live on GitHub Pages.

You never edit `white-papers.html` by hand.
You never assign your own ID.

---

## Part 9 — Self-Validation

This document has an `acg-paper:` frontmatter block. If the parser
processes this file, it appears in the index as:

```
✓ Paper Auto-Index Standard (ACG-STD-AUTOPARSE-2026)
  Type: Standard
  Tags: automation, github-actions, indexing, white-papers, standards
```

The standard indexes itself. The format describes the format.

---

*AI Craftspeople Guild · Paper Auto-Index Standard · v1.0*
*"the bot is the librarian — you are the author"*
