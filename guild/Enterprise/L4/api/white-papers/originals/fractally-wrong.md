---
title: Avoid Being Fractally Wrong
slug: fractally-wrong
authors: [Alex Bunardzic]
publication_date: Apr 06, 2026
summary: Fail early, fail often
status: position
site_href: fractally-wrong.html
---

**Kent Beck famously said that if everything goes according to the plan, we haven't learned anything.**

Now, to some people that sounds surprising. Wouldn't we want everything to go according to the plan? I mean, what's the point of making a plan if we don't want that plan to be fulfilled.

Here is where we come to a very interesting point: success is almost always liaising with learning. Endeavouring based on already learned and confirmed practices and processes is safe and secure, but cannot truly buy us much competitive advantage. The reason those practices and processes are safe and secure lies in the fact that many others have tried them and thus our competition possesses the same tools as we do. In such case, all that's left for us to do is to compete on the pricing. Which invariably means race to the bottom.

So, to avoid such race to the bottom, we need to adopt a bit of risk. Meaning, we must make ourselves open to learning. And that means that our plan, which we have made at the point when we did not learn anything new, must be challenged by what may come next once we start executing on that plan.

We thus must hope that not everything goes according to the plan (because if it does, we are sliding down the "race to the bottom" slope, and that sliding process ain't pretty).

**Avoid Being Fractally Wrong.**

## Failure-Centric Approach

Adopting the fail-first approach is an excellent way to learn new things. We start from a broken situation, we then fix it, which then enables us to conceive of the next failure. Progressing in that fashion, we are uncovering the domain by inviting and collecting and examining feedback. Great stuff.

However, that failure-centric approach is not without its perils. Today, I will briefly discuss one pernicious danger of such failure-centric approach - fractal wrongness.

## What Is Fractal Wrongness

The term "fractal wrongness" is generally attributed to Keunwoo Lee. The core observation: it's not just a wrong conclusion built on sound reasoning - it's wrong conclusions built on wrong premises built on wrong assumptions, recursively.

In other words, fractal wrongness is when someone's position is wrong at every level of resolution - zoom into any supporting argument and that's also wrong, and the arguments supporting that are wrong, all the way down. Like a fractal, the wrongness is self-similar at every scale.

## When Does Fractal Wrongness Thrive And How To Fix It?

Most often, fractal wrongness thrives in situations when assumptions are never made explicit.

The recommended way to fix that wrongness is to resort to some of the AI Craftspeople Guild's AI Rituals. AI Ritual number 5 ("Force Explicit Assumptions") offers the following advice:

If the model is making assumptions, make it say them out loud. Hidden assumptions are where most prompt drift begins.

Once assumptions are visible, you can confirm, reject, or narrow them before they contaminate the rest of the exchange.

Another reason for the emergence of fractal wrongness is if nobody on the team asks for the failure mode. That fractal wrongness can be fixed by following the AI Ritual number 3 ("Ask For The Failure Mode"):

Before accepting the happy path, ask the team how the proposed answer could fail. This shifts the interaction from affirmation to examination.

Quality of work improves when the model is used to surface breakpoints, missing assumptions, and likely regressions before implementation.

Also, fractal wrongness tends to occur when validation is social rather than empirical (the so-called "sycophancy loop").

Lastly, there is also so-called "Scheherazade Loop in human form" - plausible-sounding reasoning that survives for 45 minutes because nobody ran the tests.

The antidote to all those possible occurrences of fractal wrongness is Popperian: you don't try to verify the whole structure. You pick ONE falsifiable claim at the base and test it. If the foundation crumbles, you don't need to audit every floor.

Occam's Razor at work!
