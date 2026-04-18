# /controls

Control-plane subsystems.  One directory per control facility — each owning
its own tag namespace(s), UDTs, Jython 2.7 provider, and subsystem index.

```
controls/
  scada/             🖥️  tag plant · HMI monitor · dense-token specs (§0 — §4)
    errors/          ⚠  gateway-log ring buffer · owns errors.*
    gateway/         🛰  SCADA gateway host (loads modules)
      auth/          🔑  identity module · owns auth.* + sub-providers
  hmi/               🖼  ISA-101 operator interface: layers, palette, faceplates
    chat/            💬  P2P chat screen · owns chat.* room.* tracker.* peers.* signal.*
  plc/               🔧  GitPLC universal PLC namespace + UDT templates (git/)
  sandbox/           🧪  browser-only tool workshops (web-llm, voice, VFS) · owns sandbox.*
  db/                🗄️  tags.json — canonical snapshot read by the README HMI
  docs/standards/    📐  Konomi meta-standard + GitPLC standard (all layers)
```

Siblings (future — room here for more):

- `controls/alarm/`        alarm engine + journal (ISA-18.2 lifecycle)
- `controls/schedule/`     cron-like scheduling of broadcasts / re-announces
- `controls/routing/`      rule-based tag routing + transformations
- `controls/pinning/`      "pinned tags" (persist across sessions)

Every control subsystem follows the standard provider contract
(see `/index/README.md`): `provider.py` (Jython 2.7) + `udts.json` +
`tags.json` + `index.html` → rendered via `/index/renderer.js`.

The SCADA `gateway/` is the host for modules that own a tag namespace —
auth is the first such module.  See `controls/scada/gateway/README.md`.
