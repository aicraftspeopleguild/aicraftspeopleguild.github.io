# Level 1 — Sensing & Control

> Webhook handlers, form endpoints, event routers. Typed as `Tag` UDTs.
> See [ISA-95 L1 spec](../../../docs/engineering/architecture/isa-95/level-1-sensing.md).

## What lives here

| Asset             | Location                                        |
|-------------------|-------------------------------------------------|
| GitHub workflows  | `.github/workflows/*.yml` (must stay there)     |
| Action scripts    | `.github/scripts/*.js`                          |
| Submission form   | `forms/submit/` (moved from guild/web/submit/)  |
| Signature form    | inline in `index.html` (Google Form action)     |
| Form JS helpers   | `guild/Enterprise/L2/hmi/web/home.js` (signatories loader)        |
| Tag UDT template  | `guild/Enterprise/L3/components/udts/templates/path.udt.json` (Path is a typed route) |

## Event → Tag flow

Each L1 sensor produces a `Tag` UDT:

```json
{ "path": "github/pr/17/merged", "value": true, "quality": "good", "ts": 1745000000000 }
```

Emitters (git/forms) don't interpret events — they just produce typed
signals. Interpretation is L2's job (PackML supervision).
