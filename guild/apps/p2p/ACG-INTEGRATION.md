# P2P Guild App — Integration Notes

*Imported from [teslasolar/ACGP2P](https://github.com/teslasolar/ACGP2P) · April 2026*

This directory holds the ACGP2P project — a peer-to-peer, serverless,
SCADA-instrumented chat mesh — as a Guild app under `guild/apps/p2p/`.

## What's inside

| Path        | Purpose                                          |
|-------------|--------------------------------------------------|
| `index.html` + `index/` | Entry point: P2P chat landing + subsystem sitemap |

The control-plane (SCADA, HMI, PLC, DB, sandbox, docs) that used to live
under `guild/apps/p2p/controls/` was moved to
[`guild/Enterprise/controls/`](../../Enterprise/controls/) so it can be
shared across Guild apps. See [`guild/Enterprise/README.md`](../../Enterprise/README.md)
for the ISA-95 level mapping of those assets.

## Cross-tree wiring

After the move, this app's pages reach the controls tree at
`../../Enterprise/controls/…`. Updated references live in:

- `index.html` — landing cards + script imports
- `index/index.html` — sitemap (`ctrlRoot` constant)
- `index/renderer.js` — `mesh-bridge.js` import + `SHELL_LINKS[0].href`

`guild/Enterprise/controls/index.html` and `controls/db/index.html`
reach back to this app via relative `../../apps/p2p/` links for the
"⚒ mesh" home shortcut.

## Relation to the main Guild site

- **Separate app**: self-contained; deployed alongside the main site
  under `/guild/apps/p2p/` on GitHub Pages
- **Shares Konomi**: both use Konomi base primitives (Value, Quality,
  Timestamp, …). Upstream repo is the source of truth for Konomi
- **Shares ISA-95 controls**: now via `guild/Enterprise/controls/` rather
  than a private copy

## Upstream sync

This import is a snapshot from ACGP2P `main` as of the integration
commit. To pull future changes:

```
cd /tmp && git clone https://github.com/teslasolar/ACGP2P.git
# copy app-shell pieces:
cp -r /tmp/ACGP2P/index.html      /path/to/repo/guild/apps/p2p/
cp -r /tmp/ACGP2P/index/          /path/to/repo/guild/apps/p2p/
# copy controls into the Enterprise layer:
cp -r /tmp/ACGP2P/controls/.      /path/to/repo/guild/Enterprise/controls/
# re-apply the path fixes documented in the "Cross-tree wiring" section.
```

Consider a future submodule or subtree merge when upstream stabilizes.

## App UDT

See `guild/apps/p2p/acg-app.json` for the App UDT instance that
registers this app in the Guild catalog, and
`guild/web/components/udts/instances/paths/p2p.json` for the route.

## Known stale references

The following files still reference the old `controls/…` path as
documentation (not runtime-critical):

- `index/README.md` — example path strings in prose
- `index/docks/*.template.html` — reference-shape template documents
- `index/page.template.html` — reference-shape template document

Update these opportunistically; they do not affect runtime.

