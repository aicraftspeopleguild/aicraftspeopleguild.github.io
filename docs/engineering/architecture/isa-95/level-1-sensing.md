# Level 1 — Sensing & Control

*The interface between the physical Guild (L0) and the automation stack (L2+).*

## Sensors (inputs)

| Event                 | Source                         | Sample rate          |
|-----------------------|--------------------------------|----------------------|
| git commit            | GitHub webhook                 | Per push             |
| PR opened / synced    | GitHub `pull_request` event    | Per PR action        |
| PR merged             | GitHub `push` to main          | Per merge            |
| Manifesto sign        | Google Form submit             | Per submission       |
| Submission form       | `/guild/Enterprise/L1/forms/submit/` POST      | Per submission       |
| Paper file modified   | Workflow path filter           | Per PR               |
| Ingest run kick-off   | `.github/workflows/paper-index`| Per trigger event    |

## Actuators (outputs)

| Action                | Channel                              |
|-----------------------|--------------------------------------|
| PR comment            | GitHub `issues.createComment` API    |
| Status check          | GitHub `statuses` API                |
| Branch commit         | `git push` in Action runner          |
| Redeploy to Pages     | GitHub Pages publish pipeline        |
| Dashboard update      | Writing to `papers.json` / `state/*` |

## Raw events are Tag UDTs

Every L1 event fits the Ignition `Tag` shape:

```json
{ "path": "github/pr/17/merged", "value": true, "quality": "good", "ts": 1745000000000 }
```

This lets the supervisory layer (L2) treat every sensor uniformly:
a stream of `(path, value, quality, ts)` tuples.

## Sensing guarantees

- **Idempotent**: each Action is safe to re-run; repeated events don't
  double-publish.
- **Timestamped**: every Tag carries a UTC ms epoch so L2–L4 can
  reconstruct the order of events.
- **Quality-tagged**: `stale` / `bad` signal degraded reads; downstream
  logic must handle them (e.g., show "last known" values).

## Boundaries

L1 does **not**:

- Validate editorial quality (that's MES/L3).
- Track who signed the manifesto (that's ERP/L4).
- Run the state machine (that's SCADA/L2).

L1 only converts physical events into typed, timestamped signals.
