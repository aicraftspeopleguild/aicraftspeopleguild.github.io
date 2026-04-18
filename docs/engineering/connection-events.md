# Connection & API events · tag + script-event catalogue

Every connection-state transition in the mesh is reflected as a tag
write. Every tag write that crosses a configured edge fires a
`@tag-event` script. This file enumerates the catalogue so scripts,
dashboards, and external tooling (MQTT client, MCP server) share one
vocabulary.

Naming convention: `<namespace>.<instance>.<field>` where namespace is
one of `tracker`, `signal`, `peer`, `room`, `api`, `packml`,
`pipeline`, `script`.

## Tracker layer

`tracker.trackers.<idx>` · UDT `TrackerEndpoint`
- fields: `url`, `state` (`offline|connecting|connected`), `rttMs`, `lastAt`
- written by: `publishTrackers()` in `p2p.js`
- fires on transition: `tracker.trackers.<idx>.state from=* to=connected` → any script listening for tracker-up events
- fires on transition: `tracker.trackers.<idx>.state from=connected to=*` → flap-detector script

`tracker.current` · UDT `Tracker`
- fields: `url`, `state` (overall), `connectedAt`, `announces`, `lastAnnounceAt`, `connectedCount`, `configuredCount`
- `tracker.current.state` is the single source of truth for the badge
- fires: `tracker.current.state from=* to=connected` (cold boot complete), `from=connected to=reconnecting` (flap), `from=* to=offline` (total outage)

`tracker.state`, `tracker.count`, `tracker.announces` · scalar mirrors
of the fields above, kept for shields/readme widgets.

## Signal layer

`signal.last` · UDT `SignalEvent`
- fields: `kind` (`offer|answer`), `dir` (`in|out`), `peerId`, `offerId`, `ts`
- written on every offer/answer in `p2p.js onOffer` / `onAnswer`
- fires: `signal.last` changes with every SDP exchange — useful for
  debugging stuck handshakes.

`signal.offersIn`, `signal.answersOut`, `signal.answersIn` · Counters
incremented per event (already used by the scada.gateway status panel).

## Peer layer

`peer.<peerId>` · UDT `Peer`
- fields: `id`, `name`, `emoji`, `joinedAt`, `lastMsgAt`, `dataChannels`
- written by `peers.wire()` in `peers.js`
- fires: `peer.<peerId> from=none to=connected` (datachannel open),
  `peer.<peerId> from=connected to=none` (channel close).

Currently missing — **gaps to fill in the MQTT-layer PR**:
- `peer.<peerId>.iceState` (new/checking/connected/failed/disconnected/closed)
- `peer.<peerId>.dcState`  (connecting/open/closing/closed)
- `peer.<peerId>.rtt`      (periodic `getStats()` ping)

## Room layer

`room.data` · UDT `Room` · everything below rolls up into it.
`room.name`, `room.hash`, `room.joinedAt`, `room.peerCount`

## API watcher layer

Files under `guild/Enterprise/L3/automation/instances/apis/*.json`
each define an `Api` UDT with `url`, `watch_field`, `output_tag`,
`interval_s`. The runtime polls the URL, compares `watch_field`, and
writes `output_tag` on change.

Currently wired:
- `api.health.paperCount`  from `/api/health.json:paperCount`
- `api.state.faults_active` from `/api/state.json:summary.faults_active`

Each of these fires `on_transition` script events on value change. The
state-machine smoke test (`bin/sm-test.py --tag api.health.paperCount
--to CHANGED`) currently reports 0 matches because no @tag-event
header listens on them yet — that's an opportunity, not a bug.

## PackML layer

`packml.current` · current state (`EXECUTE`, `HOLDING`, …)
`packml.state.updated` · CHANGED token fired on every transition
- currently consumed by `build-programs:on-packml-state-updated`
- the `build-packml-statechart.py` organism reads `packml.current` to
  position its halo.

## Proposed @tag-event triggers (for the MQTT/MCP follow-up)

```
# tracker.current.state → raise fault when all trackers fall
{
  "id": "tracker-outage:on-all-offline",
  "listens": {"kind":"on_transition","tag":"tracker.current.state","from":"*","to":"offline"},
  "action": {"tool_id": "faults:raise", "inputs": {"code":"TRACKER_OUTAGE"}}
}

# api.health.paperCount → regen paper feed + roulette
{
  "id": "paper-feed:on-paperCount-changed",
  "listens": {"kind":"on_transition","tag":"api.health.paperCount","from":"*","to":"CHANGED"},
  "action": {"tool_id": "build:svg", "inputs": {"targets":["paper-feed","paper-roulette"]}}
}

# peer.<*>.state=connected → handshake logger
{
  "id": "peer-log:on-connect",
  "listens": {"kind":"on_transition","tag":"peer.*.state","from":"*","to":"connected"},
  "action": {"tool_id": "log:info", "inputs": {"event":"peer-up"}}
}
```

The `*` in `tag: peer.*.state` is a new wildcard the matcher doesn't
support yet — adding it is part of the MQTT-pub/sub PR.

## MQTT mapping (follow-up PR)

- MQTT **topic** ≡ tag path
- MQTT **message** ≡ tag value + quality + ts
- MQTT **QoS 0** ≡ in-memory pub/sub
- MQTT **QoS 1** ≡ tag write → GH-Issues-backed durable store
- MQTT **retained** ≡ most recent value (what `TAG.read()` returns today)

## MCP mapping (follow-up PR)

The MCP server will expose:
- `tag_read(path)`, `tag_write(path, value, type?, quality?)` wrapping `gh_tag`
- `fire_event(tag, from, to, kind?)` wrapping `state_machine.fire_event`
- `cmd_action(id)` wrapping the control-deck action catalogue
- `ls_scripts(tag?)` enumerating @tag-event subscribers

So an external agent can do everything the README buttons do, but
through a typed schema.
