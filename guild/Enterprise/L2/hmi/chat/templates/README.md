# chat/templates

Copy-and-fill template library for the chat subsystem.  Follows the same
**Konomi dense-token** shape as the HMI templates (see
`/controls/hmi/templates/README.md`) and the **/index/** udt + tags schema.

```
templates/
  udts.template.json           reference shape of /{sub}/udts.json — chat-flavoured
  tags.template.json           reference shape of /{sub}/tags.json — chat-flavoured
  wire/                        over-the-wire DataChannel envelopes
    hi.template.json           handshake on channel open
    msg.template.json          regular chat message
    ping.template.json         keepalive / RTT probe
    ack.template.json          delivery receipt
    typing.template.json       typing indicator (transient)
  ui/                          HMI faceplates bound to chat tags (mirrors controls/hmi/templates/faceplate)
    peer.faceplate.json        one peer row in the peer list
    room.faceplate.json        room header card
    tracker.faceplate.json     tracker health pill
    mesh.faceplate.json        aggregate mesh summary (peers + trackers + signal)
```

## Wire envelopes

Every envelope is a plain object with a discriminator `t`:

```jsonc
{ "t": "<kind>", "id": "<peerId>", "ts": <ms>, ... }
```

- `hi`    — identity + capability exchange on every open DataChannel
- `msg`   — user-authored text
- `ping`  — empty beat, used for RTT + liveness
- `ack`   — receipt for a specific `msg.id`
- `typing` — transient "typing…" indicator (ignored if stale > 3 s)

## Token budget

Every file is kept **under 250 tokens** so any envelope shape or faceplate
can be dropped into an LLM prompt whole.
