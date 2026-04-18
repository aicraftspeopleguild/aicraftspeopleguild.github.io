# Google Form Spec — Article Submissions

Field-by-field spec for the Google Form that collects submissions
when authors can't open a PR. Create the form at docs.google.com,
then paste the form-action URL into `guild/Enterprise/L1/forms/submit/index.html`.

## Fields

| Field                 | Type         | Required | Validation                              |
|-----------------------|--------------|----------|-----------------------------------------|
| Author Name           | short-answer | yes      | non-empty                               |
| Author Email          | short-answer | yes      | email regex                             |
| Affiliation           | short-answer | no       | —                                       |
| Article Title         | short-answer | yes      | ≤ 120 chars                             |
| Article Type          | dropdown     | yes      | one of 6 enum values                    |
| Abstract              | paragraph    | yes      | 60–400 words                            |
| Body (Markdown)       | paragraph    | yes      | ≥ 800 / ≥ 300 words per type            |
| Tags (comma-separated)| short-answer | no       | —                                       |
| Citations / Links     | paragraph    | no       | —                                       |
| AI Assistance?        | dropdown     | yes      | none / light / substantial              |
| License Agreement     | checkbox     | yes      | must be checked (CC-BY 4.0)             |
| Originality Attest    | checkbox     | yes      | must be checked                         |

## Destination

Link the form to a Google Sheet named `ACG-Submissions`. Each row =
one submission. A GitHub Action (future: `article-ingest.yml`) polls
the sheet daily and produces `submissions/incoming/<id>.yml` PRs.

## Settings

- **Responses**: require sign-in = off (public submissions allowed)
- **Allow response editing**: off (submissions are immutable once posted)
- **Confirmation message**: "Thank you. Your submission enters review.
  A Guild member will be in touch within 7 days."

## Webhook-style: acg-paper frontmatter output

The form post-processor converts each row into YAML matching the
Paper Auto-Index Standard:

```yaml
acg-paper:
  title: "<Article Title>"
  author: "<Author Name> (<Affiliation>)"
  type: <article_type>
  abstract: "<Abstract>"
  tags: [<tags...>]
  status: draft
  ai_assistance: <level>
```

No `id`, `date`, or `slug` — the auto-indexer fills those.
