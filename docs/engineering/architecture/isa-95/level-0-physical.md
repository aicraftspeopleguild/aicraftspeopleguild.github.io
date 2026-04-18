# Level 0 — Physical Process

*The actual human work. The Guild exists because people do these things.*

## What happens at L0

- An author reads, thinks, writes a draft paper
- Guild members run a mob programming session
- A reviewer reads a draft and forms a judgment
- A signatory reads the manifesto and decides whether to endorse it
- A craftsperson writes code with AI assistance, evaluates, accepts or rejects
- A ritual is practiced (e.g., falsify-before-ship)

## Physical artefacts

| Artefact           | Where it lives (pre-ingest)                  |
|--------------------|----------------------------------------------|
| Paper draft        | Author's editor; Google Doc; Markdown file   |
| Mob session        | A room or a Tuple/Pop session                |
| Review notes       | Margin annotations, chat logs                |
| Ritual experiment  | Personal notes; a dev journal                |
| Decision to sign   | In the signatory's own mind                  |

## Why it matters

ISA-95 Level 0 is the irreducible source of value. Everything uphill
(sensors, SCADA, MES, ERP) exists to serve, observe, or account for
L0 — never replace it.

For the Guild specifically:

- The papers indexed at L4 are only ever representations of L0 thinking.
- The PackML pipeline at L2 never produces a paper; it only transports one.
- Automation failures at L1–L3 degrade but do not destroy L0 value —
  an author's draft on their laptop survives any API outage.

## Design rule

> Every higher-level process must have a meaningful degraded mode when
> deprived of Level 0 input. No L1+ automation should be allowed to
> generate apparent L0 value — that's the "sleazy shilling" failure the
> Manifesto forbids.

Corollary: AI assistance is Level 0 tooling, not Level 0 substitute.
The craftsperson remains the author.
