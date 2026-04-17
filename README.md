# aicraftspeopleguild.github.io

The public website of the **AI Craftspeople Guild (ACG)** — a professional community advocating for quality, integrity, and human judgement in AI-assisted software development.

🌐 **Live site:** [aicraftspeopleguild.github.io](https://aicraftspeopleguild.github.io)
📜 **Manifesto:** [Read it here](https://aicraftspeopleguild.github.io/aicraftspeopleguild-manifesto.html)
⚒ **Org:** [github.com/aicraftspeopleguild](https://github.com/aicraftspeopleguild)

---

## Overview

This is a static, build-free site: plain HTML + CSS with a small amount of JS. It is the Guild's public front door — the place where the manifesto, charter, rituals, peer review protocol, member profiles, white papers, and lessons live.

The site is hand-crafted on purpose. No framework, no bundler, no dependency tree. The look-and-feel is a shared palette (parchment, ink, rust, bronze, graphite) with Playfair Display and Work Sans, so new pages drop in next to existing ones without a design system fight.

## Key Sections

**Foundational documents**
- [Manifesto](aicraftspeopleguild-manifesto.html) — what the Guild stands for
- [Charter](charter.html) — how the Guild governs itself
- [Code of Conduct](code-of-conduct.html) — how members treat one another
- [Mission Statement](mission-statement.html) — why the Guild exists

**Practices and lessons**
- [AI Rituals](ai-rituals.html) — repeatable habits for prompting and review
- [Mob Programming 101](mob-programming.html) — one problem, one keyboard, many minds
- [ACG Peer Reviews](acg-peer-reviews.html) — the Guild's review protocol
- [AI Harness](ai-harness.html) — engineering guardrails around AI output

**Thinking and critique**
- [White Papers](white-papers.html) — longer-form Guild writing
- [Hall of Fame](hall-of-fame.html) / [Hall of Shame](hall-of-shame.html) — examples worth studying, good and bad
- [Showcases](showcases.html) — member work worth seeing

**People**
- [Members](members.html) — individual member profiles
- [Chief AI Skeptic Officer](chief-ai-skeptic-officer.html) — the role every AI-using team needs

## Tech Stack

The codebase is deliberately simple:

- **HTML** — one file per page, self-contained styles where it helps readability
- **CSS** — shared palette via CSS custom properties, no preprocessor
- **JavaScript** — only where it earns its keep (forms, light interactions)
- **Markdown** — `docs/` and a handful of notes

No build step. No `node_modules`. No lockfile. If you can open a file in a text editor, you can contribute.

## Getting Started

Clone and serve locally:

```bash
git clone https://github.com/aicraftspeopleguild/aicraftspeopleguild.github.io.git
cd aicraftspeopleguild.github.io
python3 -m http.server 8000
# then open http://localhost:8000/
```

Or just open `index.html` in a browser — most pages work without a server.

## Contributing

The Guild grows through member contribution. A few patterns the site follows:

1. **One HTML file per page.** Link it from `index.html`'s top nav and, where it fits, from related pages.
2. **Reuse the palette.** The CSS custom properties at the top of each page (`--color-parchment`, `--color-ink`, `--color-rust`, etc.) keep new pages visually consistent.
3. **Lessons have a hero, a structure, and a call to action.** See [`ai-rituals.html`](ai-rituals.html) and [`mob-programming.html`](mob-programming.html) for the shape.
4. **Member profiles live at the root** as `firstname-lastname.html` and link from [`members.html`](members.html).
5. **Keep it craft-visible.** Hand-written HTML beats auto-generated HTML here — a reader should be able to open View Source and learn something.

Open an issue or a pull request on this repo. For larger discussions, use the [Guild Discussions tab](https://github.com/aicraftspeopleguild/aicraftspeopleguild.github.io/discussions).

## Repository Layout

```
├── index.html                      # front page + manifesto + signature form
├── *.html                          # lesson pages, member profiles, white papers
├── main.css                        # shared site styles
├── member-profile.css              # member page styles
├── docs/
│   ├── api-design.md               # internal design notes
│   ├── htmx-patterns.md            # patterns we've tried
│   └── popcorn-flow-slides.*       # popcorn-flow deck
├── *.png / *.jpg / *.jpeg / *.mp4  # images and media for pages
└── README.md                       # this file
```

## License

Content © 2026 AI Craftspeople Guild. The Guild welcomes reading, sharing, and thoughtful response. For reuse of written Guild content beyond fair use, please open an issue and ask — we usually say yes.

---

⚒ **Kindness, consideration, and respect.** ⚒
