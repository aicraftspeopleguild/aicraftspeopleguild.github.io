---
acg-paper:
  id: ACG-ARCH-SITEMAP-2026
  type: standard
  title: "Root Index Routing + Sitemap"
  author: "AI Craftspeople Guild"
  date: 2026-04-18
  status: published
  tags: [sitemap, routing, navigation, architecture]
  abstract: >
    How the root index.html maps to every addressable resource in the
    Guild site — public SPA routes, operator dashboard, apps, APIs,
    originals, and per-directory assets.
---

# Root Index Routing + Sitemap

## Two front doors

```
https://aicraftspeopleguild.github.io/
│
├─ /                         PUBLIC  index.html (manifesto + nav + sign form)
│  │
│  ├─ #/manifesto            SPA route — renders into #app mount
│  ├─ #/charter              "
│  ├─ #/code-of-conduct      "
│  ├─ #/mission              "
│  ├─ #/white-papers         "
│  ├─ #/rituals              "
│  ├─ #/mob-programming      "
│  ├─ #/flywheel             "
│  ├─ #/showcases            "
│  ├─ #/members              "
│  ├─ #/hall-of-fame         "
│  ├─ #/hall-of-shame        "
│  └─ #manifesto, #sign      in-page anchors (smooth scroll)
│
└─ /guild/                   OPERATOR  guild/index.html (internal dashboard)
   │
   ├─ apps/
   │  ├─ whitepapers/        Per-paper App UDTs + rendered cards
   │  ├─ p2p/                ACGP2P mesh chat (self-contained)
   │  └─ test/               ACG-TEST runner fixtures
   │
   ├─ Enterprise/L0/           README + paper / member markdown originals
   ├─ Enterprise/L1/            README + forms/submit/
   ├─ Enterprise/L2/              README + state/*.state.json
   ├─ Enterprise/L3/                README (build pipeline doc)
   ├─ Enterprise/L4/
   │  ├─ api/papers.json     Public read API (Paper[])
   │  ├─ api/members.json    Public read API (Member[])
   │  ├─ api/health.json     Vitals {paperCount, memberCount, lastUpdated}
   │  ├─ runtime/tags.json   Konomi Value live-tag snapshot
   │  ├─ csv/*.csv           Dense CSV catalogs (papers, tags, runs, …)
   │  └─ database/           SQLite schemas (acg.db is gitignored)
   │
   ├─ Enterprise/controls/   Imported Konomi + ISA-95 tree
   │
   └─ web/
      ├─ white-papers/       Paper markdown originals + UDT instances
      ├─ members/<slug>/     Per-member dir (portrait + profile)
      ├─ components/         Registry + UDT instances for view components
      ├─ views/              View tree templates
      ├─ pages/              Page UDT instances (route ↔ view)
      ├─ perspective/        Ignition-style view authoring
      ├─ scripts/            11-step build pipeline + CI helpers
      ├─ style/              Site CSS
      ├─ assets/             Static images
      ├─ home.js             Signatories loader + form handler
      ├─ renderer.js         Client-side SPA view engine
      ├─ site-map.json       Machine-readable route table
      └─ dist/               Build artefacts (gitignored; p-*.html etc.)
```

## URL → resolver

| URL pattern                                        | Resolver                                      |
|----------------------------------------------------|-----------------------------------------------|
| `/`                                                | Public SPA shell (built from `guild/web/perspective/views/index.view.json`) |
| `/#/<slug>`                                        | `renderer.js` — fetches page + view + data JSONs by matching the Path UDT route |
| `/guild/`                                          | Operator dashboard (built from `guild/web/perspective/views/guild-index.view.json`) |
| `/guild/apps/<name>/`                              | Static HTML served directly                   |
| `/guild/Enterprise/L4/api/*.json`                         | Static JSON API (regenerated each build)      |
| `/papers.json`                                     | Flat API catalog (auto-index workflow output) |
| `/guild/web/white-papers/originals/<slug>.md`      | Paper source of truth (markdown)              |
| `/guild/web/members/originals/<slug>.md`           | Member profile markdown                       |

## Source of truth

- **Path UDT instances** at `guild/web/components/udts/instances/paths/*.json` — 46 Path records define every registered route
- **`guild/web/site-map.json`** — machine-readable route table consumed by `renderer.js`
- **`guild/web/components/udts/instances/paths/_graph.json`** — 46 nodes, 45 edges dependency graph
- **`/sitemap.xml`** at repo root — SEO sitemap auto-generated from Path UDTs
- **This document** — human-readable overview

## How a click resolves

Example: visitor clicks "Charter" from the public home page.

```
1. <a href="#/charter"> in the north dock nav
2. Browser updates URL to /#/charter
3. hashchange event fires
4. renderer.js currentRoute() returns "/charter"
5. matchRoute against site-map.json → Path UDT "charter"
6. fetch pages/charter.page.json → view + data refs
7. fetch views/charter.view.json + views/data/charter.data.json
8. fetch all referenced component JSONs (once, cached)
9. renderNode walks the tree, binds props, produces HTML
10. body gains has-route class → CSS hides static body sections, shows #app
11. rendered output injected into #app mount
```

No new URL. No full page reload. SEO is served by the statically-rendered
`guild/web/dist/*.html` pages + the new `sitemap.xml`.
