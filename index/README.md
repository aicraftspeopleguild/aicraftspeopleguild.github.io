# /index — sources for the root index.html

Everything the root `index.html` is **made of**, co-located at the repo
root. Sibling of `index.html` itself.

## Layout

```
aicraftspeopleguild.github.io/
├── index.html              rendered shell (generated from index/view.json)
├── index/
│   ├── view.json           Perspective-style view — source of truth
│   ├── manifest.json       machine-readable inventory of deps
│   ├── deps.view.json      Perspective view that renders deps.html
│   ├── deps.html           human-readable deps dashboard (generated)
│   ├── docks/
│   │   ├── north.view.json sticky top (nav + emblem + h1 + subtitle)
│   │   ├── body.view.json  home body (context, manifesto grid, sign form, CTA, worship zone)
│   │   └── south.view.json sticky bottom (footer chrome)
│   └── README.md           this file
```

The builder (`guild/web/scripts/perspective-build.js`) scans this
directory recursively alongside `guild/Enterprise/L2/hmi/web/perspective/views/` and
emits each non-partial view to its `custom.output` path.

## Path UDT

Home route (`/`) is registered by:
  `guild/Enterprise/L2/hmi/web/components/udts/instances/paths/home.json`

It carries `page: "index/view.json"` so every downstream tool (sitemap,
path-graph, bin/acg navigation) resolves the home route back to this
directory's authored source.

## Editing

To change the home page:

1. Edit `index/view.json` (or one of the docks for nav/footer).
2. Run `./README.sh perspective` — rebuilds `index.html` at root.
3. (Optional) `./README.sh test:links` to verify.

`index/docks/*.view.json` are marked `custom.partial: true` so they
are NOT emitted as standalone HTML. They're composed into
`index/view.json` via the dock-layout slots.
