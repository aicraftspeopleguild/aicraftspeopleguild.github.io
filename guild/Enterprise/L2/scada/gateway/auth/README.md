# /controls/scada/gateway/auth

Identity + sign-in module hosted by the SCADA gateway.  Owns the `auth.*`
namespace; each OAuth provider owns its own sub-namespace beneath it.

```
controls/scada/gateway/auth/
  provider.py         top-level · owns auth.profile + auth.signedIn
  udts.json           general UDTs (Profile)
  tags.json           auth.* tag catalog
  index.html          subsystem index (rendered by /index/renderer.js)
  webrtc/             📡 cryptographic peer-id identity (no OAuth, no server)
  webtorrent/         🌊 tracker-based peer discovery (info_hash as bearer)
  discord/            🎮 implicit-grant OAuth (pure browser, no proxy)
  github/             🐙 device flow (requires a CORS proxy)
  google/             🔎 OIDC implicit / id_token (stub · not wired yet)
```

## Namespace map

```
auth.profile            Profile UDT · whichever provider succeeded last
auth.signedIn           bool · derived from auth.profile
auth.webrtc.*           peer-id identity (anonymous cryptographic)
auth.webtorrent.*       tracker discovery state (info_hash, trackers[], announce)
auth.discord.*          discord-specific state (client id, last token age, …)
auth.github.*           github-specific state (device code in flight, ...)
auth.google.*           google-specific state
```

**Identity vs OAuth.**  `webrtc` + `webtorrent` are *passive* identity
providers — no human-facing sign-in flow, but the peer id and the tracker
info_hash function as bearer tokens that prove mesh membership.  Discord
/ GitHub / Google are traditional OAuth flows that attach a human
identity (display name, avatar) on top.

## Sub-provider contract

Each provider directory follows the §0 section contract:

```
<provider>/udts.json      provider-specific UDTs (DiscordProfile, etc.)
<provider>/tags.json      auth.<provider>.* tag catalog
<provider>/provider.py    Jython 2.7 · owns auth.<provider>.*
```

A successful sign-in there writes:
  1. `auth.<provider>.profile` (their local snapshot)
  2. `auth.profile` at the top level (the canonical "who is signed in")
  3. `auth.signedIn = true`

On `logout()` the provider clears `auth.<provider>.*` AND if it was the
last-write owner of `auth.profile`, clears that too.
