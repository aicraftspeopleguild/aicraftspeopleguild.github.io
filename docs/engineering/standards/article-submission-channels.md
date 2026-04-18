# Article Submission — Channels

Three accepted paths, in priority order.

## 1. Pull Request (preferred)

Author opens a PR adding their `.md` or `.html` to the repo with
`acg-paper:` frontmatter. The auto-indexer (`.github/workflows/paper-index.yml`)
validates and rebuilds the index on every push.

Best for: Guild members, technical authors comfortable with git.

## 2. Google Form

Hosted Google Form collects the required fields from non-technical
authors. On submit, a script (see `docs/engineering/standards/google-form-spec.md`)
pulls responses into `submissions/incoming/*.yml` for an editor to
convert into a PR.

Best for: first-time contributors; guest authors without a GitHub account.

## 3. Site-Hosted HTML Form

`guild/l1-sensing/forms/submit/index.html` — a static form on the Guild site that
posts submissions via a Google Forms action (same backend as channel 2)
so no server is required.

Best for: one-click contributions from the public site. Same downstream
flow as the Google Form.

## What happens next (all channels)

```
submission
   │
   ▼
[auto-indexer] ── validates required fields + quality bar
   │             (from article-submission.md)
   │
   ├── PASS ──► draft status, PR opened for review
   │
   └── FAIL ──► bot comment lists missing criteria
```

No submission bypasses the minimum criteria. The channel is just
a collection mechanism; the bar is identical.
