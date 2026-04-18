# controls/scada/gateway/styles

🎨  **Gateway-managed stylesheets** — single source of truth for HMI
visual consistency across every page in the project.

```
styles/
  theme.css       parchment-warm design tokens (--bg, --tx, --tl, --r-md, …)
  style.css       layout for the main chat page (index.html)
  section.css     subsystem-index theme (consumed by /index/renderer.js)
```

## Contract

- Every HMI page links **`controls/scada/gateway/styles/theme.css`** (or
  `section.css`, which `@import`s theme.css).
- Per-tool overrides (e.g. `controls/sandbox/shared/sandbox.css`) MUST
  `@import` from this directory rather than redefining tokens.
- New themes go here so the HMI palette stays consistent with
  `controls/docs/standards/konomi/isa101/ColorMeaning.udt.json`.

## Reference paths

From any HMI page, the shortest relative path to `theme.css` is:

| Page location                              | Path |
|--------------------------------------------|------|
| `/index.html` (landing)                             | `controls/scada/gateway/styles/theme.css` |
| `/controls/scada/gateway/{gateway-log,health}.html` | `./styles/theme.css` |
| `/controls/hmi/chat/index.html`             | `../../scada/gateway/styles/theme.css` |
| `/controls/index.html`                      | `./scada/gateway/styles/theme.css` |
| `/controls/{hmi,plc,db}/index.html`         | `../scada/gateway/styles/theme.css` |
| `/controls/scada/index.html`                | `./gateway/styles/theme.css` |
| `/controls/scada/errors/index.html`         | `../gateway/styles/theme.css` |
| `/controls/scada/gateway/index.html`        | `./styles/theme.css` |
| `/controls/scada/gateway/auth/index.html`   | `../styles/theme.css` |
| `/controls/sandbox/web-llm/index.html`      | `../../scada/gateway/styles/theme.css` |
