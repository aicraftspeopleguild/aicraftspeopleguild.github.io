# gh_tag — GitHub Issues as a dynamic tag DB

Every tag is one GitHub Issue in the target repo. Its title encodes the
tag path, its body holds the latest Value/Quality/Timestamp, and each
comment is an append-only history record.

## Convention

| element | shape | example |
|---|---|---|
| title | `tag:<path>` | `tag:live.sprint-counter` |
| body | JSON in a ```json code fence | `{"value":3,"quality":"good","type":"Counter","updated_at":"2026-04-18T…","description":"current sprint"}` |
| labels | `tag`, `ns:<namespace>` | `tag`, `ns:live` |
| comments | one per update, same JSON shape | rolls up into `read().value` |

## Tools

```bash
python bin/acg gh-tag:list               # all tags in the repo
python bin/acg gh-tag:list ns=live       # just the `live` namespace

python bin/acg gh-tag:read path=live.sprint-counter

# writes need GITHUB_TOKEN with `public_repo` (or `repo`) scope
export GITHUB_TOKEN=ghp_…

python bin/acg gh-tag:init  path=live.sprint-counter value=3 type=Counter description="current sprint"
python bin/acg gh-tag:write path=live.sprint-counter value=4
```

## How to seed from the GitHub UI

Open a new issue with:

- **Title**: `tag:live.sprint-counter`
- **Body**:
  ````
  ```json
  {"value": 3, "quality": "good", "type": "Counter", "description": "current sprint"}
  ```
  ````
- **Labels**: `tag`, `ns:live` (create the labels if they don't exist)

`gh-tag:read` / `gh-tag:list` pick it up immediately via the public
search + issues API — no auth needed for reads.

## Repo selection

Defaults to `aicraftspeopleguild/aicraftspeopleguild.github.io`. Override:

```bash
GH_TAG_REPO=teslasolar/aicraftspeopleguild.github.io python bin/acg gh-tag:list
```

## Rate limits

- Unauthenticated: 60 req/hr (read-only)
- Authenticated: 5000 req/hr

`gh-tag:read` makes 1 request (+1 if the issue has comments); `list_tags`
is one request per 100 issues; `write` makes 3 (find + comment + patch).
