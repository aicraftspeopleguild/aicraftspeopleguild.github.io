---
title: 🌸 ASS-OS BLOOM PROMPT — OCCAM
slug: occams-razor
authors: [Bloom Prompt, "Occam's Razor", Guild Archive]
summary: The Razor That Shaves ItselfThis document has one argument. Every ring is the same argument. The repetition IS the proof.
status: knowledge-about-knowledge
site_href: occams-razor.html
---

**SEED**

The simplest explanation that accounts for all the evidence is probably correct. Everything else in this document is that sentence again, wearing different clothes. If you stopped reading here you'd have the whole thing. The fact that you didn't stop is why the razor exists.

## R0 — THE RAZOR IN ONE LINE

```
Given competing hypotheses, select the one
with the fewest assumptions.
— William of Ockham, ~1323
```

That's it. That's the razor. 700 years old. 12 words. Still the most powerful debugging tool ever invented. Everything below this line is technically unnecessary. But you're still reading. Because humans don't trust simplicity. We think if it's short it must be incomplete. The razor cuts that instinct too.

## R1 — THE RAZOR BY EXAMPLE

A child has a fever, sore throat, and a rash.

```
HYPOTHESIS A (3 assumptions):
  The child has an allergic reaction AND
  a separate viral infection AND
  a skin condition triggered by stress.

HYPOTHESIS B (1 assumption):
  The child has strep throat.

Strep causes: fever, sore throat, and scarlatina rash.

Occam says: run the strep test first.
```

### 80085 BLOOM — MEDICAL OCCAM

```
RING 3 (FORM):
  One pathogen. Three symptoms. Test the one thing.

RING 5 (FLOW):
  1. List all symptoms
  2. Find the single cause that explains the most
  3. Test THAT cause first
  4. If confirmed → treat
  5. If not → add complexity ONE assumption at a time

RING 19 (EDGE):
  Refuses to order 3 specialist referrals
  when 1 throat swab explains all 3 symptoms.

RING 281 (SOUL):
  The parent spent 4 months rotating between
  allergist, dermatologist, and ENT
  because nobody ran the 30-second swab first.
```

## R2 — THE RAZOR IN CODE

```
# BAD: 47 lines, 3 imports, 2 abstractions
import re
from collections import defaultdict
from itertools import chain

def find_duplicates_complex(lst):
    seen = defaultdict(int)
    for item in chain(lst):
        normalized = re.sub(r'\s+', ' ', str(item).strip().lower())
        seen[normalized] += 1
    return {k: v for k, v in seen.items() if v > 1}

# GOOD: 1 line, 0 imports, 0 abstractions
def find_duplicates(lst):
    return {x for x in lst if lst.count(x) > 1}
```

Both work. One has 3 assumptions (regex needed, defaultdict needed, chain needed). One has zero assumptions. The razor picks the second one. Not because short is always better. Because **assumptions are always debt.**

### 80085 BLOOM — CODE OCCAM

```
RING 3 (FORM):
  Fewer abstractions. Fewer imports. Fewer failure points.

RING 5 (FLOW):
  1. Write the simplest version that passes the test
  2. Measure if it's actually too slow
  3. If yes → add ONE optimization
  4. If no → ship it
  5. The premature optimization was the extra assumption

RING 19 (EDGE):
  Refuses to add a caching layer before proving
  the uncached version is too slow.

RING 281 (SOUL):
  The 47-line version exists because the programmer
  was afraid the simple version was "too simple."
  The fear of simplicity IS the complexity.
```

## R3 — THE RAZOR IN DEBUGGING

Your application crashes every Tuesday at 3 AM.

```
HYPOTHESIS A (5 assumptions):
  A race condition in the thread pool AND
  a memory leak that accumulates over 7 days AND
  a timezone bug in the cron scheduler AND
  a kernel-level file descriptor exhaustion AND
  cosmic rays.

HYPOTHESIS B (1 assumption):
  The Tuesday 3 AM cron job runs out of disk space
  because the weekly log rotation happens at 3 AM
  on Tuesday.

df -h
> /var/log  98% full

Occam wins in 4 seconds.
```

The five-assumption developer spent three sprints building monitoring dashboards. The one-assumption developer ran `df -h`.

### 80085 BLOOM — DEBUG OCCAM

```
RING 3 (FORM):
  One command. One observation. One fix.

RING 5 (FLOW):
  1. Reproduce the failure
  2. List what changed (time, data, state)
  3. Find the ONE thing that correlates
  4. Test that ONE thing
  5. If it explains everything → fix it and go home

RING 19 (EDGE):
  Refuses to open the profiler before checking
  if the disk is full.

RING 281 (SOUL):
  Three sprints of monitoring infrastructure
  because nobody ran df -h.
```

## R4 — THE RAZOR IN ARCHITECTURE

Your team proposes a microservices architecture: 12 services, 3 message queues, 2 databases, a service mesh, a custom API gateway, and a Kubernetes cluster.

The application has 4 endpoints and 200 users.

```
HYPOTHESIS A (12 assumptions):
  Each domain needs its own service AND
  services need async communication AND
  data needs polyglot persistence AND
  traffic needs a service mesh AND
  deployment needs orchestration AND
  [7 more assumptions about future scale]

HYPOTHESIS B (1 assumption):
  One server. One database. One deploy.

The application has 4 endpoints and 200 users.
A $5/month VPS handles 10,000 concurrent connections.
You have 200 users.
```

The razor doesn't say microservices are wrong. The razor says: **you're solving problems you don't have yet with assumptions you can't validate.**

### 80085 BLOOM — ARCHITECTURE OCCAM

```
RING 3 (FORM):
  Monolith until proven otherwise.

RING 5 (FLOW):
  1. Build the simplest thing that works
  2. Measure actual load
  3. Identify the ONE bottleneck
  4. Extract THAT bottleneck into a service
  5. Repeat only when the next bottleneck appears

RING 19 (EDGE):
  Refuses to add Kubernetes for 200 users.

RING 281 (SOUL):
  The 12-service architecture was designed
  for a million users that never came.
  The monolith served the 200 users
  that actually showed up.
```

## R5 — THE RAZOR IN RELATIONSHIPS

She's not texting back.

```
HYPOTHESIS A (4 assumptions):
  She saw the text AND
  she's playing games AND
  she's testing your response time AND
  she's talking to someone else.

HYPOTHESIS B (1 assumption):
  She's busy.
```

The razor doesn't guarantee B is correct. The razor says: **exhaust the simple explanation before constructing the complex narrative.** The complex narrative feels more satisfying because it gives you a villain. The simple explanation gives you nothing to fight. That's why we resist it. That's why the razor is necessary.

## R6 — THE RAZOR ON ITSELF

```
HYPOTHESIS A:
  You need 7 rings, 5 sub-blooms, 6 examples
  across medicine, code, debugging, architecture,
  and relationships to understand Occam's Razor.

HYPOTHESIS B:
  "Given competing hypotheses, select the one
   with the fewest assumptions."
  — R0, line 1 of this document.
```

You already had it. You had it at R0. Everything after R0 was assumption on top of assumption. More examples. More domains. More words. This document VIOLATES its own thesis. Deliberately. Because the violation IS the lesson.

You didn't trust the 12-word version. You needed proof. You needed examples. You needed to see it work in medicine, code, debugging, architecture, and relationships before you believed that 12 words could carry the weight.

That distrust of simplicity is EXACTLY what the razor cuts.

## R7 — THE RECURSION

```
The simplest explanation of Occam's Razor
is Occam's Razor.

"Fewer assumptions."

The fact that this document exists
is proof that we don't believe it.

The fact that you read to the end
is proof that you need to.

The razor shaves itself.
And grows back.
And you shave it again.
Every morning.
For the rest of your life.

Because complexity is the beard.
And it always grows back.
And the razor is always 12 words.
And 12 words is always enough.
And you'll always want more.

And that's the razor.
```

*given competing explanations*

*select the one*

*with the fewest assumptions*

*this was always the whole document*

*the rest was the beard*

**🪒 和**
