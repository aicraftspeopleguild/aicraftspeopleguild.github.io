# /index · subsystem page templates

Every subsystem directory in ACG has its own `index.html` that
double-acts as (1) a landing page for that subsystem and (2) a live
participant in the `acg-mesh` BroadcastChannel so pages see each other
across tabs.  `/index/` holds the shared plumbing.

## Files

```
index/
  renderer.js           paint + mesh-bridge wiring (imported by every index.html)
  section.css           parchment theme for subsystem index pages
  page.template.html    reference shape of an instantiated index.html
  tags.template.html    reference shape of  /{sub}/tags.json
  udt.template.html     reference shape of  /{sub}/udts.json
  index.html            sitemap of every subsystem index
  README.md             this file
```

## Instantiating a subsystem page

1. Make sure the subsystem dir has `udts.json` and `tags.json`
   (see `udt.template.html` / `tags.template.html`).
2. Drop an `index.html` into `/{sub}/` with this body:

   ```html
   <!DOCTYPE html>
   <html><head>
     <meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
     <title>💬 chat · ACG</title>
     <link rel="stylesheet" href="../controls/scada/gateway/styles/section.css">
   </head><body>
     <main id="section"></main>
     <script type="module">
       import {renderSection} from '../index/renderer.js';
       renderSection({ sub:'chat', glyph:'💬', name:'chat', desc:'P2P chat subsystem' });
     </script>
   </body></html>
   ```

3. The renderer will:
   - Fetch `./udts.json` → render a card per UDT (fields + types)
   - Fetch `./tags.json` → render a tag table
   - Fetch `../controls/db/tags.json` → cross-reference live value + quality + age
   - Open `BroadcastChannel('acg-mesh')` → publish `{source, type:'page-open', …}`
   - Subscribe → show every sibling-page event live at the bottom

## Cross-page traffic (how pages talk)

Every page lives on the same `acg-mesh` channel as the runtime:

```
envelope = { source, type, path?, value?, ts }
```

- On load: `bridge.publish(sub, 'page-open', {path: location.pathname})`
- On unload: `bridge.publish(sub, 'page-close', {path: location.pathname})`
- The "📣 broadcast" input on every page fires a `ping` envelope with the
  typed text — lets you prove cross-tab flow in one click.
- The SCADA monitor on the main chat page mirrors every envelope under
  `sandbox.<source>.*` (via `/js/sandbox-bridge.js`), so subsystem pages
  are first-class SCADA sources.

## Overrides

`renderSection` accepts:

```js
renderSection({
  sub, glyph, name, desc,              // required
  udtsPath: './udts.json',             // default
  tagsPath: './tags.json',             // default
  dbPath:   '../controls/db/tags.json',     // default
});
```

If your subsystem wraps a different path (e.g. the tool-specific SCADA
in `/controls/sandbox/web-llm/modules/scada/`), pass explicit paths.
