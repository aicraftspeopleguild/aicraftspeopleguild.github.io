# Test Guild App — Integration Notes

*Imported from [teslasolar/ACG-Test](https://github.com/teslasolar/ACG-Test) · April 2026*

This directory holds the ACG-TEST project — the reference implementation of
the **Konomi Standard** (UDT-nested architecture for GitHub Actions testing) —
as a Guild app under `guild/apps/test/`.

## What's inside

| Path                              | Purpose                                                  |
|-----------------------------------|----------------------------------------------------------|
| `index.html`                      | Entry point: app landing                                 |
| `pages/standard.html`             | The full Konomi standard                                 |
| `pages/types.html`                | Per-UDT reference with live `<udt-*>` elements           |
| `pages/example.html`              | Article-notification rendered as UDTs                    |
| `pages/runner.html`               | In-browser test dashboard                                |
| `pages/terminal.html`             | Browser-side test terminal                               |
| `assets/style.css`                | Shared styles                                            |
| `assets/udt-elements.js`          | Custom elements: `<udt-expectation>` etc.                |
| `assets/runner-core.js`           | Pure parser + check functions                            |
| `assets/test-runner.js`           | Page bootstrap that mounts results                       |
| `assets/terminal.js`              | Terminal command engine                                  |
| `tests/manifest.json`             | List of test files                                       |
| `tests/*.test.yml`                | One test per page / workflow                             |
| `paper-auto-index-standard.html`  | Guild paper (acg-paper frontmatter)                      |
| `papers.json`                     | Machine-readable paper index (generated upstream)        |
| `white-papers.html`               | Human-readable paper index (generated upstream)          |
| `acg-test.config.yml`             | Runner config + extension notes                          |
| `README.md`                       | Upstream README                                          |

## What was stripped on import

- `.git/` — upstream history is not part of this site
- `.github/workflows/` — upstream's `deploy-pages.yml` and `paper-index.yml`
  belong to the upstream repo's CI; they are not run from this site

## Relation to the main Guild site

- **Separate app**: self-contained; deployed alongside the main site under
  `/guild/apps/test/` on GitHub Pages
- **Reference for the test standard**: Guild members can link to runnable
  Konomi UDT examples from white papers and engineering docs
- **Independent of the renderer**: this app does not use
  `guild/Enterprise/L2/hmi/web/renderer.js` — it is a static sub-site

## Upstream sync

This import is a snapshot from ACG-Test as of the integration commit. To pull
future changes:

```
cd /tmp && git clone https://github.com/teslasolar/ACG-Test.git
cp -r /tmp/ACG-Test/. /path/to/aicraftspeopleguild.github.io/guild/apps/test/
rm -rf /path/to/aicraftspeopleguild.github.io/guild/apps/test/.git
rm -rf /path/to/aicraftspeopleguild.github.io/guild/apps/test/.github
```

Consider a future submodule or subtree merge when upstream stabilizes.

## App UDT

See `guild/apps/test/acg-app.json` for the App UDT instance that registers
this app in the Guild catalog, and
`guild/Enterprise/L2/hmi/web/components/udts/instances/paths/test.json` for the route.
