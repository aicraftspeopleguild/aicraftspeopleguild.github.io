# Level 4 — Enterprise (ERP)

*The business of the Guild. Long-horizon state: manifesto, membership, catalog, governance, public API.*

## What ERP owns

| Domain            | Source of truth                                  |
|-------------------|--------------------------------------------------|
| Manifesto         | `guild/Enterprise/L2/hmi/web/perspective/views/index.view.json`    |
| Membership roster | `guild/web/members/udts/instances/*.json` + Google Sheet signatories |
| Paper catalog     | `guild/Enterprise/L4/api/white-papers/udts/instances/*.json`   |
| Governance        | Charter, Code of Conduct, Mission Statement      |
| Public API        | `guild/Enterprise/L4/api/{papers,members,health}.json`     |
| Taxonomy          | `guild/Enterprise/L4/api/white-papers/tags/index.json`         |

## The Guild enterprise schema

ERP data lives in two parallel forms:

1. **UDT instances** — JSON files, git-versioned, source of truth.
2. **SQLite mirror** — `guild/Enterprise/L4/database/acg.db`, rebuilt from the JSON
   on every build. Supports queries, joins, reports.

Tables:

| Table            | Level-4 question it answers                          |
|------------------|------------------------------------------------------|
| `papers`         | What have we published, when, by whom?               |
| `paper_authors`  | Who wrote what (many-to-many)                        |
| `paper_tags`     | Taxonomy — what topics do we cover?                  |
| `members`        | Who is in the Guild?                                 |
| `member_tags`    | What expertise do members bring?                     |
| `member_papers`  | Which members have authored which papers?            |
| `programs`       | What automation do we operate? (links to MES/L3)     |
| `packml_runs`    | Audit trail — did the pipeline run cleanly?          |

## API v1.0 as ERP external interface

The public `/api/` endpoints (ACG-STD-API-2026) are the **ERP REST layer**:

- `/api/papers.json` — full catalog, read-only
- `/api/members.json` — roster, read-only
- `/api/health.json` — enterprise vitals

Writes happen via PR (through MES/L3), never directly to the API.

## Governance rules (business logic)

- A paper moves from `draft` → `review` → `published` via editorial
  workflow, never by direct API write.
- Membership is gated by signing the manifesto or opening a profile PR.
- Type/status enums are fixed vocabularies defined in the UDT templates.
- CC-BY 4.0 license applies to all published papers by default.
- AI assistance disclosure is a mandatory field on submission.

## Cross-enterprise integration

The ERP layer exposes:

- **GitHub Organization** — authoritative identity (membership gate)
- **Cloudflare Worker** (future) — MCP server for AI agents
- **GitHub Pages** — static site delivery
- **Google Forms / Sheets** — signatory ingestion (channel 2 of submissions)

## ERP does not

- Schedule work (MES/L3 does that).
- Run processes (SCADA/L2 does that).
- React to raw events (Sensing/L1 does that).
- Author content (Physical/L0 does that).
