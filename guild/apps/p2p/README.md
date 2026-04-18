# ⚒ ACG P2P · guild mesh

*AI Craftspeople Guild · peer-to-peer, serverless, SCADA-instrumented chat plant.*

<a href="https://teslasolar.github.io/ACGP2P/"><img alt="chat"       src="https://img.shields.io/badge/⚒-open_chat-1a5c4c?style=for-the-badge&labelColor=faf6f0"></a>
<a href="https://teslasolar.github.io/ACGP2P/sandbox/"><img alt="sandbox" src="https://img.shields.io/badge/🧪-sandbox-6f42c1?style=for-the-badge&labelColor=faf6f0"></a>
<a href="https://teslasolar.github.io/ACGP2P/sandbox/web-llm/"><img alt="web-llm" src="https://img.shields.io/badge/🧠-web--llm-c47a20?style=for-the-badge&labelColor=faf6f0"></a>
<a href="https://teslasolar.github.io/ACGP2P/controls/scada/gateway/gateway-log.html"><img alt="log" src="https://img.shields.io/badge/⚠-gateway_log-b85c5c?style=for-the-badge&labelColor=faf6f0"></a>
<a href="https://teslasolar.github.io/ACGP2P/controls/scada/gateway/health.html"><img alt="health" src="https://img.shields.io/badge/⚕-health-4a8868?style=for-the-badge&labelColor=faf6f0"></a>
<a href="https://teslasolar.github.io/ACGP2P/controls/hmi/chat/#scada"><img alt="scada" src="https://img.shields.io/badge/🖥️-scada-79c0ff?style=for-the-badge&labelColor=1c2128"></a>

![Pages](https://img.shields.io/github/deployments/teslasolar/ACGP2P/github-pages?label=pages&color=1a5c4c)
![Last commit](https://img.shields.io/github/last-commit/teslasolar/ACGP2P?label=last%20commit&color=1a5c4c)
![Issues](https://img.shields.io/github/issues/teslasolar/ACGP2P?label=issues&color=c47a20)
![License](https://img.shields.io/github/license/teslasolar/ACGP2P?color=8d95a0)

---

## 📡 Live plant readout

Badges below read [`controls/db/tags.json`](https://github.com/teslasolar/ACGP2P/blob/main/controls/db/tags.json) on every render.  Edit that file
(or use one of the [issue forms](#-controls) below) and the HMI updates.

### 💬 chat

![peers](https://img.shields.io/badge/dynamic/json?url=https://teslasolar.github.io/ACGP2P/controls/db/tags.json&query=%24.room.peerCount.value&label=room.peerCount&color=1a5c4c&style=flat-square)
![room](https://img.shields.io/badge/dynamic/json?url=https://teslasolar.github.io/ACGP2P/controls/db/tags.json&query=%24.room.name.value&label=room&color=1a5c4c&style=flat-square)
![msgsIn](https://img.shields.io/badge/dynamic/json?url=https://teslasolar.github.io/ACGP2P/controls/db/tags.json&query=%24.chat.msgsIn.value&label=chat.msgsIn&color=4a8868&style=flat-square)
![msgsOut](https://img.shields.io/badge/dynamic/json?url=https://teslasolar.github.io/ACGP2P/controls/db/tags.json&query=%24.chat.msgsOut.value&label=chat.msgsOut&color=4a8868&style=flat-square)

### 📡 tracker · signalling

![tracker](https://img.shields.io/badge/dynamic/json?url=https://teslasolar.github.io/ACGP2P/controls/db/tags.json&query=%24.tracker.state.value&label=tracker.state&color=c47a20&style=flat-square)
![announces](https://img.shields.io/badge/dynamic/json?url=https://teslasolar.github.io/ACGP2P/controls/db/tags.json&query=%24.tracker.announces.value&label=tracker.announces&color=c47a20&style=flat-square)
![offersIn](https://img.shields.io/badge/dynamic/json?url=https://teslasolar.github.io/ACGP2P/controls/db/tags.json&query=%24.signal.offersIn.value&label=signal.offersIn&color=8d95a0&style=flat-square)
![answersOut](https://img.shields.io/badge/dynamic/json?url=https://teslasolar.github.io/ACGP2P/controls/db/tags.json&query=%24.signal.answersOut.value&label=signal.answersOut&color=8d95a0&style=flat-square)

### 🔑 identity · ⌖ version

![signedIn](https://img.shields.io/badge/dynamic/json?url=https://teslasolar.github.io/ACGP2P/controls/db/tags.json&query=%24.auth.signedIn.value&label=auth.signedIn&color=1a5c4c&style=flat-square)
![sha](https://img.shields.io/badge/dynamic/json?url=https://teslasolar.github.io/ACGP2P/controls/db/tags.json&query=%24.version.shortSha.value&label=version.shortSha&color=1c2128&style=flat-square)
![rateLimited](https://img.shields.io/badge/dynamic/json?url=https://teslasolar.github.io/ACGP2P/controls/db/tags.json&query=%24.version.rateLimited.value&label=version.rateLimited&color=b85c5c&style=flat-square)

### ⚠ errors · 🧪 sandbox

![errors](https://img.shields.io/badge/dynamic/json?url=https://teslasolar.github.io/ACGP2P/controls/db/tags.json&query=%24.errors.count.value&label=errors.count&color=b85c5c&style=flat-square)
![err-ERROR](https://img.shields.io/badge/dynamic/json?url=https://teslasolar.github.io/ACGP2P/controls/db/tags.json&query=%24.errors.byLevel.ERROR.count.value&label=ERROR&color=b85c5c&style=flat-square)
![err-WARN](https://img.shields.io/badge/dynamic/json?url=https://teslasolar.github.io/ACGP2P/controls/db/tags.json&query=%24.errors.byLevel.WARN.count.value&label=WARN&color=c47a20&style=flat-square)
![sandbox](https://img.shields.io/badge/dynamic/json?url=https://teslasolar.github.io/ACGP2P/controls/db/tags.json&query=%24.sandbox.bridgeOpen.value&label=sandbox.bridgeOpen&color=6f42c1&style=flat-square)

---

## 🎛 Controls

Every button below is a pre-filled GitHub issue form — filing it writes to the
DB.  The sync workflow ([`.github/workflows/sync-db.yml`](.github/workflows/sync-db.yml))
picks each one up and commits the merged JSON back to `main`.

[![Write a tag](https://img.shields.io/badge/🏷️-write_tag-1a5c4c?style=for-the-badge&labelColor=faf6f0)](../../issues/new?template=tag-update.yml)
[![Log incident](https://img.shields.io/badge/⚠-log_incident-b85c5c?style=for-the-badge&labelColor=faf6f0)](../../issues/new?template=log-entry.yml)
[![Control action](https://img.shields.io/badge/🎛-control_action-c47a20?style=for-the-badge&labelColor=faf6f0)](../../issues/new?template=control-action.yml)

<details><summary>Open issue templates directly</summary>

- [`tag-update.yml`](.github/ISSUE_TEMPLATE/tag-update.yml) — `🏷️ <path> = <value>`, quality, type, note
- [`log-entry.yml`](.github/ISSUE_TEMPLATE/log-entry.yml)   — `⚠ [<LEVEL>] <msg>` with optional stack / meta
- [`control-action.yml`](.github/ISSUE_TEMPLATE/control-action.yml) — clear-log · rotate-tracker · join-room · pin/unpin-tag · force-reannounce · toggle-monitor · custom

</details>

---

## 🧬 Architecture

```mermaid
flowchart LR
  subgraph browser [browser]
    CHAT[💬 chat]
    AUTH[🔑 auth]
    VER[⌖ version]
    ERR[⚠ errors]
    SCADA[🖥️ SCADA]
    SBX[🧪 sandbox]
  end
  BUS((🛰️ acg-mesh))
  DB[(🗄️ db / tags.json)]
  BADGES[shields.io badges]
  FORMS[issue forms]

  CHAT --> SCADA
  AUTH --> SCADA
  VER --> SCADA
  ERR --> SCADA
  SBX --> BUS
  BUS --> SCADA
  SCADA -.-> DB
  DB --> BADGES
  FORMS -.-> DB
```

---

## 📁 Repo layout

```
⚒ ACGP2P/
├─ index.html            🏠  operator dashboard / landing
├─ controls/             🎛  control-plane subsystems
│   ├─ scada/              🖥️  owns sys.* version.* + dense manifests (§0—§4)
│   │   ├─ 00-legend.json  …  04-sandbox.json       declarative specs
│   │   ├─ programs/           per-module dense-glyph specs
│   │   ├─ errors/         ⚠  owns errors.*  (gateway-log area)
│   │   └─ gateway/        🛰  SCADA gateway host
│   │       ├─ styles/         theme.css · style.css · section.css   (HMI consistency)
│   │       ├─ scripts/        runtime ES modules (main · ui · config · p2p · peers · chat · auth · version · errors · sandbox-bridge · scada/*)
│   │       ├─ providers/      registry.json — canonical tag-provider registry
│   │       └─ auth/       🔑  identity module · owns auth.* (webrtc/webtorrent/discord/github/google)
│   ├─ hmi/                🖼  ISA-101 operator interface (layers, palette, faceplates)
│   │   └─ chat/             💬  P2P chat HMI screen · owns chat.* room.* tracker.* peers.* signal.*
│   ├─ plc/                🔧  GitPLC universal PLC namespace (git/ UDT templates)
│   ├─ sandbox/            🧪  browser-only tools · owns sandbox.*
│   │   └─ web-llm/          🧠 voice-powered in-browser LLM
│   ├─ db/                 🗄️  tags.json (HMI source) · README.md
│   └─ docs/standards/     📐  Konomi meta-standard + GitPLC standard
├─ .github/
│   ├─ ISSUE_TEMPLATE/   tag-update · log-entry · control-action
│   └─ workflows/        sync-db.yml
```

---

## 🌐 Glyphs · type shorthand

See [`controls/scada/00-legend.json`](https://github.com/teslasolar/ACGP2P/blob/main/controls/scada/00-legend.json) for the full decompressor.
Every manifest in this repo uses the same grammar:

| glyph | meaning | glyph | meaning |
|---|---|---|---|
| 🏗️ | UDT | 📋 | provider |
| 📦 | instance | 🏷️ | tag |
| 🔌 | channel | 🖥️ | HMI |
| 💬 | chat   | 🧪 | sandbox |
| 👥 | peer   | 🧠 | LLM |
| 📡 | tracker | 🎤 | voice |
| 🔀 | commit | 💜 | emotion |
| 📁 | file   | 🛰️ | mesh bridge |
| 🔑 | identity | ⚙️ | config |
| 🟢 🟡 🔴 | tag quality | 和 | resonant / complete |

---

## 🏗️ Quick start

```bash
# serve locally (no build)
python3 -m http.server 8000
open http://localhost:8000/
```

Or just visit **<https://teslasolar.github.io/ACGP2P/>** and the mesh finds its peers.

---

## 📄 License

MIT · © AI Craftspeople Guild
