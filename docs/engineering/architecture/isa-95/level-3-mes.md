# Level 3 — Manufacturing Operations (MES)

*Scheduling, dispatching, editorial workflow, documentation — the "what runs when and why".*

## What MES owns

MES (ISA-95 L3) turns ERP directives (L4) into scheduled work executed
via SCADA (L2). For the Guild:

| MES responsibility         | Implementation                                    |
|----------------------------|---------------------------------------------------|
| **Work scheduling**        | `.github/workflows/*.yml`                         |
| **Dispatching**            | `guild/web/scripts/build.sh` (11-step orchestrator) |
| **Documentation control**  | `docs/engineering/` — specs, ADRs, standards      |
| **Editorial workflow**     | PR review + auto-index + status transitions       |
| **Quality management**     | `test-links.py`, `test-browser.js`, `test-nav.js` |
| **Traceability**           | PackML run history + git history                  |

## The Guild MES workflows

### W1 — Paper submission workflow

```
author submits (PR | Google Form | HTML form)
   ↓
[paper-index.yml] parse-papers.js → validate → generate-html.js
   ↓
auto-commit papers.json + updated index
   ↓
reviewer(s) approve → merge to main
   ↓
[build.sh] SCADA-supervised: ingest → apps → api → dist
   ↓
live on Pages
```

### W2 — Ritual experiment workflow

```
member proposes experiment → ritual card → PR
   ↓
validation (Experiment UDT schema)
   ↓
published to ai-rituals.html
   ↓
post-period: result write-up (often a research-note paper)
```

### W3 — Member onboarding workflow

```
signatory submits manifesto form → members.json appended
   ↓
(optional) opens PR for full profile page
   ↓
[paper-index.yml] includes them in members list
   ↓
API health.json count increments
```

## Document control

The `docs/engineering/` tree is itself under MES control:

| Area                    | What it contains                                    |
|-------------------------|-----------------------------------------------------|
| `standards/`            | ACG-STD-* numbered standards (process contracts)    |
| `architecture/`         | ACG-ARCH-* architecture records (this doc!)         |
| `tech-spec/`            | ACG-TS-* implementation specs                       |
| `component-catalog/`    | ACG-CC-* UI components                              |
| `templates/`            | UDT source of truth in 6 languages                  |

Every doc carries an `acg-paper:` frontmatter block so it's indexed as
a `Document` UDT — self-describing MES content.

## MES does not

- Execute the work (that's L2 via PackML).
- Own the roster of signatories (that's L4 membership catalog).
- Generate physical output (that's L0 authoring).
