# White Papers Pipeline

A small SCADA-style intake pipeline for Guild white papers. Drop a file into `originals/`, run `ingest.py`, and the parser produces a JSON instance of the **WhitePaper UDT** under `udts/instances/` and updates `tags/index.json`. Already-ingested files are skipped by sha256 hash, so the script is safe to re-run.

## Layout

```
white-papers/
├── README.md                    # this file
├── ingest.py                    # parser — scans originals/, emits instances
├── index.json                   # manifest of loaded sources + produced instances
├── originals/                   # drop white papers here in any supported format
│   ├── *.md                     # markdown with YAML front-matter
│   ├── *.csv                    # one paper per row, field names match UDT params
│   └── *.html                   # rendered pages (title + stripped body)
├── udts/
│   ├── templates/
│   │   ├── white-paper.udt.json # WhitePaper UDT type definition
│   │   └── tag.udt.json         # Tag UDT type definition
│   └── instances/               # generated — one JSON per paper
└── tags/
    └── index.json               # generated — tag catalog with paper_ids + counts
```

## How To Add A White Paper

1. Drop a source file into `white-papers/originals/`. Name it however you like — the slug is derived from the title (or from an explicit `id:` front-matter field).
2. Run:
   ```bash
   python3 white-papers/ingest.py
   ```
3. Commit the new original plus the generated `udts/instances/*.json`, updated `index.json`, and `tags/index.json`.

The script is stdlib-only — no `pip install` step.

## Supported Source Formats

### Markdown (`.md`) — with front-matter

```markdown
---
title: AI Harness
authors: Alex Bunardzic
publication_date: 2026-03-09
doc_number: ACG-WP-003-2026
source_medium: site-only
summary: Change architecture layer constraining autonomous code evolution.
tags: [ai-harness, architecture, governance]
status: published
site_href: ai-harness.html
---

The body of the paper in plain markdown goes here. It can be short
(abstract-only) or the whole paper.
```

Front-matter keys map directly to UDT `parameters`. `authors` and `tags` accept either YAML-style lists or comma-separated strings.

### CSV (`.csv`) — one paper per row

Column names must match UDT parameter names. At minimum include `title` and `authors`. Example:

```csv
title,authors,publication_date,doc_number,tags,summary,site_href
The Prediction Trap,Alex Bunardzic,2026-02-18,ACG-WP-002-2026,"prediction,uncertainty",Why point-forecast culture fails under AI-assisted delivery,the-prediction-trap.html
The Harm Equation,Alex Bunardzic,2026-02-22,ACG-WP-004-2026,"ethics,risk",A working formula for assessing product harm,the-harm-equation.html
```

Multi-value cells (`authors`, `tags`) may be `;`- or `,`-separated if the cell itself is quoted.

### HTML (`.html`)

For white papers already rendered as full HTML pages. The ingester extracts `<title>` / first `<h1>` and strips tags for the body. Prefer markdown for new papers; HTML support exists so existing rendered papers can round-trip.

## The WhitePaper UDT

A **UDT** (User Defined Type, borrowed from Ignition / SCADA) is a template with **parameters** (authored fields) and **tags** (system-derived fields). Every generated instance conforms to `udts/templates/white-paper.udt.json`:

- **Parameters**: `title`, `authors`, `publication_date`, `doc_number`, `source_medium`, `summary`, `tags`, `status`, `site_href`.
- **Tags**: `id` (slug), `original_path`, `original_format`, `original_hash_sha256`, `body`, `instance_path`, `ingested_at`, `schema_version`.

This shape lets downstream consumers (the Guild site, linting, search, cross-linking) iterate over a uniform `instances/*.json` directory without re-parsing originals.

## Idempotence & Change Detection

`index.json` records the sha256 of every source file plus which slugs it produced. On each run:

- Unchanged sources → skipped.
- New or modified sources → re-parsed, instances rewritten.
- Source removed → its instance(s) deleted, index entry removed.

`tags/index.json` is always rebuilt from the current set of instances, so tag counts and `paper_ids` stay in sync without manual bookkeeping.

## Submission Flow (rough sketch)

The pipeline is designed so that a future submission surface (form, issue template, email drop) can land a file into `originals/` and a CI job runs `ingest.py`. Until that exists, drop files in by hand and open a PR.

## Versioning

The UDT template carries a `version` field. Each generated instance records its `schema_version` so instances can be migrated if the template evolves.
