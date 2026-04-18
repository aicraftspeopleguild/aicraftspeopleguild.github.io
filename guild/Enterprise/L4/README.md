# Level 4 — Enterprise (ERP)

> Master data: manifesto, roster, paper catalog, governance, public API.
> See [ISA-95 L4 spec](../../../docs/engineering/architecture/isa-95/level-4-erp.md).

## What lives here

| Asset                      | Path                                                  |
|----------------------------|-------------------------------------------------------|
| SQLite database            | `database/acg.db` (gitignored; regenerable)           |
| Schema                     | `database/schema*.sql`                                |
| API endpoints              | `api/{papers,members,health}.json`                    |
| Paper UDT instances        | `guild/Enterprise/L4/api/white-papers/udts/instances/*.json`        |
| Member UDT instances       | `members/udts/instances/*.json`                       |
| Program UDT instances      | `programs/instances/*.json`                           |
| App UDT instances          | `guild/apps/whitepapers/udts/instances/*.json`        |
| Tag inverted indexes       | `.../tags/index.json` under each domain               |
| Rendered ERP surface       | `guild/web/dist/*.html` (gitignored; regenerable)     |
| Governance docs            | `docs/engineering/standards/*.md`                     |

## Master data flow

```
L3 ingest.py / extract.py
   ↓
UDT instance JSON (source of truth)
   ↓
database/init-db.py seeds acg.db
   ↓
api/scripts/build-api.py emits /api/*.json
   ↓
Public API served by GitHub Pages
```

## ERP identity & auth

- GitHub Organization membership (`aicraftspeopleguild`) gates write ops
- Public read via static JSON (no auth needed)
- Future: Cloudflare Worker MCP SSE proxy for agent access
