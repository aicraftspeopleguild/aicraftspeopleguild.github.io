# P2P Guild App — Integration Notes

*Imported from [teslasolar/ACGP2P](https://github.com/teslasolar/ACGP2P) · April 2026*

This directory holds the ACGP2P project — a peer-to-peer, serverless,
SCADA-instrumented chat mesh — as a Guild app under `guild/apps/p2p/`.

## What's inside

| Path        | Purpose                                          |
|-------------|--------------------------------------------------|
| `index.html` + `index/` | Entry point: P2P chat landing          |
| `controls/` | ISA-95 controls architecture for the app         |
| `controls/db/tags.json`     | Live runtime tag database        |
| `controls/docs/standards/konomi/` | Konomi standards (already imported at repo `docs/templates/konomi/`) |
| `controls/hmi/`   | Human-Machine Interface templates          |
| `controls/scada/` | SCADA gateway, errors, providers           |
| `controls/plc/`   | Programmable logic                         |
| `controls/sandbox/` | Experiments (web-llm, etc.)              |
| `.github/`  | Upstream's own CI — inert here (not root)        |

## Relation to the main Guild site

- **Separate app**: self-contained; deployed alongside the main site
  under `/guild/apps/p2p/` on GitHub Pages
- **Shares Konomi**: both use Konomi base primitives (Value, Quality,
  Timestamp, …). Upstream repo is the source of truth for Konomi
- **Shares ISA-95 ethos**: ACGP2P is an L0–L4 controls stack of its
  own, nested within our larger Guild enterprise (which treats this
  app itself as an L4 ERP-catalogued asset)

## Upstream sync

This import is a snapshot from ACGP2P `main` as of the integration
commit. To pull future changes:

```
cd /tmp && git clone https://github.com/teslasolar/ACGP2P.git
cp -r /tmp/ACGP2P/. /path/to/aicraftspeopleguild.github.io/guild/apps/p2p/
rm -rf /path/to/aicraftspeopleguild.github.io/guild/apps/p2p/.git
```

Consider a future submodule or subtree merge when upstream stabilizes.

## App UDT

See `guild/apps/p2p/acg-app.json` for the App UDT instance that
registers this app in the Guild catalog, and
`guild/web/components/udts/instances/paths/p2p.json` for the route.
