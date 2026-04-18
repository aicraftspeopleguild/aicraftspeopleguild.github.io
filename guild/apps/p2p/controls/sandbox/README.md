# ⚒ ACG Sandbox

Self-contained, browser-only tools that can run independent of — or alongside —
the ACG P2P mesh. Each tool lives in its own subdirectory, ships a single
`index.html` entry point, and uses the shared scaffold in `shared/`.

Lives under `/controls/sandbox/` as a control-plane subsystem.

```
controls/sandbox/
  index.html              — launcher (lists every tool)
  shared/
    sandbox.css           — common dark theme + layout primitives
    mesh-bridge.js        — BroadcastChannel bridge to the main ACG
                            SCADA tag plant (publish sandbox events
                            → `sandbox.<tool>.*` tags when the main
                            page is open in another tab)
  web-llm/                — in-browser LLM (WebGPU) + voice + VFS
    index.html
    modules/
      mcp-tools-engine.js — virtual filesystem, git-lite, LLM tool parser
```

## Adding a new tool

1. `mkdir controls/sandbox/<tool-name>/`
2. Add `index.html` with `<link rel="stylesheet" href="../shared/sandbox.css">`
3. `import {bridge} from '../shared/mesh-bridge.js'` and publish events with
   `bridge.publish('<tool>', 'event-name', payload)` so the main ACG SCADA
   monitor picks them up under `sandbox.<tool>.*`.
4. Register the tool in `controls/sandbox/index.html`'s tool list.

## Decentralized mesh power

The bridge is one-way by default (sandbox → ACG), but the main ACG app can
relay any published event across the WebTorrent-tracker peer mesh via its
existing `bcast()` — point `mesh-bridge.js`'s handler at it from
`js/main.js` to give sandbox tools true P2P reach.
