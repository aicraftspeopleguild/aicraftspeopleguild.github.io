# controls/scada/gateway/providers

📋  **Tag-provider registry** — the SCADA gateway's catalogue of every
namespace owner in the project.  Each row in `registry.json` describes
one provider: where its Jython 2.7 code lives, where its UDT + tag
catalogs live, and which `<ns>.*` paths it owns.

```
providers/
  registry.json    canonical registry — formerly /providers.json at the root
  README.md        this file
```

## Contract

- A row MUST have `id`, `dir`, `namespaces`, plus at least one of
  `provider` (Jython) or `viewer` (HTML).
- Optional: `udts`, `tags`, `browser` (ES modules), `subProviders`,
  `host`, `templates`, `standards`, `specs`, `programs`, `viewer`.
- The browser runtime in
  `controls/scada/gateway/scripts/scada/providers.js` mirrors this list
  as enums; keep them in sync.

## Adding a tag provider

1. Drop a `provider.py` (Jython 2.7) plus `udts.json` and `tags.json`
   into the subsystem directory.
2. Append a new row to `registry.json` pointing at those files and
   declaring the owned `namespaces[]`.
3. Add an `index.html` that calls `renderSection({sub, glyph, name})` —
   the renderer reads the registry row to paint the page.
4. (Optional) Add the matching enum to
   `controls/scada/gateway/scripts/scada/providers.js`.

## Future modules

- `providers/audit/`     signed audit trail of every tag write
- `providers/rbac/`      per-namespace read/write authorization
- `providers/devices/`   external device-driver registry (Modbus, OPC-UA)
