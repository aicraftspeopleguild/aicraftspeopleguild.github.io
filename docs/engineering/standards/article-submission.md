---
acg-paper:
  id: ACG-STD-SUBMIT-2026
  type: standard
  title: "Article Submission Standard"
  author: "AI Craftspeople Guild"
  date: 2026-04-18
  status: published
  tags: [standards, submission, editorial, governance]
  abstract: >
    Minimum criteria authors must meet to submit an article to the Guild.
    Defines required fields, quality bar, review path, and the three accepted
    submission channels: pull request, Google Form, site-hosted HTML form.
---

# Article Submission Standard

*ACG-STD-SUBMIT-2026 · AI Craftspeople Guild · April 2026*

## Minimum Criteria

Every submission must satisfy:

| Criterion        | Rule                                                                 |
|------------------|----------------------------------------------------------------------|
| Author           | Real identity; affiliation optional                                  |
| Type             | One of: `white-paper`, `position-paper`, `experimental`, `research-note`, `knowledge`, `standard` |
| Title            | ≤ 120 chars, sentence case                                           |
| Abstract         | 60–400 words; describes thesis, evidence, and conclusion             |
| Body             | ≥ 800 words for papers, ≥ 300 for research notes                     |
| Citations        | External claims referenced; hyperlinks or DOIs preferred             |
| Originality      | Authored by submitter; AI assistance disclosed                       |
| License          | CC-BY 4.0 unless explicitly negotiated                               |
| Format           | Markdown or HTML; PDFs require a `.meta.yml` sidecar                 |
| Frontmatter      | `acg-paper:` block per ACG-STD-AUTOPARSE-2026                        |

## Quality Bar

- Claims are falsifiable or clearly speculative (label as `experimental`).
- Disagreements with other Guild publications are cited and addressed.
- No sleazy shilling, no unsupported personal attacks, no hype.

## Review Path

1. Submission lands via one of the three channels (Part 2).
2. Auto-indexer parses frontmatter, validates fields, assigns ID.
3. At least one Guild member reviews for criteria above.
4. Status transitions `draft` → `review` → `published` (or `archived`).

See `article-submission-channels.md` for the three submission paths.
