---
acg-paper:
  id: ACG-STD-API-2026
  type: standard
  title: "ACG API v1.0"
  author: "AI Craftspeople Guild"
  date: 2026-04-18
  status: published
  tags: [api, standards, mcp, cli, github-pages]
  abstract: >
    Static-JSON API served from GitHub Pages, matching CLI, and MCP server
    spec. Zero-cost: pages.json + members.json + health.json generated on
    every PR merge; CLI fetches over HTTPS; MCP bridged via Cloudflare
    Worker (SSE).
---

# ACG API v1.0

Source: `github.com/aicraftspeopleguild/aicraftspeopleguild.github.io`
Host: `aicraftspeopleguild.github.io` (GitHub Pages)

## UDT Source of Truth

See [docs/templates/](../../templates/) — each UDT is defined once in YAML/Python/SQL/TS/JSON-Schema and code-generated per language.

## Static JSON API

| Endpoint                            | Shape                                  |
|-------------------------------------|----------------------------------------|
| `/api/papers.json`                  | `Paper[]`                              |
| `/api/members.json`                 | `Member[]`                             |
| `/api/health.json`                  | `{paperCount, memberCount, lastUpdated}` |

All three are built by `guild/web/scripts/api/build-api.py` from the SQLite DB (`guild/l4-erp/database/acg.db`) which is itself seeded from UDT instances. Each build writes to `guild/l4-erp/api/` and is served as-is from GitHub Pages.

## CLI (`acg`)

| Command                          | Action                                     |
|----------------------------------|--------------------------------------------|
| `acg papers [--tag=X] [--type=Y]`| GET `/api/papers.json` + local filter      |
| `acg members`                    | GET `/api/members.json`                    |
| `acg health`                     | GET `/api/health.json`                     |
| `acg submit <file>`              | parse `acg-paper` frontmatter → open PR    |
| `acg validate <file>`            | local frontmatter check                    |

CLI source: `bin/acg` (Python stdlib only; no deps beyond `urllib`).

## MCP Server

Remote MCP over SSE at `https://aicraftspeopleguild.github.io/mcp/sse` (Cloudflare Worker proxy; Worker calls Pages).

| Tool             | Input                                           | Behavior                        |
|------------------|-------------------------------------------------|---------------------------------|
| `list_papers`    | `{tag?, type?}`                                 | fetch + filter papers.json      |
| `get_paper`      | `{id}`                                          | lookup by id                    |
| `list_members`   | `{}`                                            | fetch members.json              |
| `search_papers`  | `{query}`                                       | keyword match title+abstract+tags |
| `submit_paper`   | `{title,author,type,abstract,content}`          | GitHub API → branch + PR        |
| `validate_paper` | `{content}`                                     | parse frontmatter → pass/fail   |
| `health`         | `{}`                                            | fetch health.json               |

## Generation flow

```
PR merged to main
   │
   ▼
.github/workflows/paper-index.yml
   │  parse *.html *.md *.meta.yml for acg-paper
   │  build papers.json, members.json, health.json, white-papers.html
   │
   ▼
commit to main → GitHub Pages serves /api/*.json
```

## Auth / Deploy

- **Auth**: GitHub OAuth → `aicraftspeopleguild` org membership gates write ops
- **Deploy**: GitHub Pages (static) + Cloudflare Worker (MCP SSE proxy)
- **Cost**: $0
