---
title: "AI Harness: Constraint-Driven Software Development for the Age of AI Agents"
authors: Alex Bunardzic
publication_date: 2026-03-09
doc_number: ACG-WP-003-2026
source_medium: site-only
summary: A change architecture layer that constrains autonomous code evolution, prevents specification drift, and keeps AI agents operating inside approved architectural boundaries.
tags: [ai-harness, architecture, governance, constraint-driven-development]
status: published
site_href: ai-harness.html
---

# AI Harness

AI-assisted development changes the problem of architecture itself. When
agents can produce plausible code at arbitrary speed, the scarce resource
stops being code production and becomes *constraint enforcement*: keeping
autonomous change inside the shape the system was designed to have.

This paper introduces the **AI Harness** as a change architecture layer
sitting between human intent and AI-generated diffs. It names the
specification, enumerates the invariants the system must preserve, and
refuses agent output that would violate them. The harness is not a linter
and not a review checklist — it is an executable description of what the
system is allowed to become.

See also: `acg-peer-reviews.html`, `ai-rituals.html`, `mob-programming.html`.
