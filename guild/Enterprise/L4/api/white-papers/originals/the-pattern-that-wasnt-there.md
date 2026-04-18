---
title: "The Pattern That Wasn't There"
slug: the-pattern-that-wasnt-there
authors: [Published on LinkedIn, Laurie Scheepers]
publication_date: 22 February 2026
summary: A gentle warning about mistaking fluency for truth
status: position
site_href: the-pattern-that-wasnt-there.html
---

There is a particular feeling that comes when an AI system hands you something that looks like a breakthrough. The form is polished. The analogy is elegant. The conclusion feels inevitable. That feeling is precisely when the epistemic bar should rise, not fall.

## What LLMs Actually Do

Large language models are trained on enormous quantities of human text. They learn, with remarkable fidelity, the rhetorical form of discovery: the cadence of a well-constructed argument, the aesthetic of mathematical proof, the tone of scientific breakthrough.

They do not perform the epistemic work that produces genuine discovery. They produce text that resembles it.

That distinction matters enormously, and it is easy to miss. A model can write LaTeX that passes visual inspection and still contain a logical error in step three that a mathematician would catch in thirty seconds. To a non-specialist, the form looks indistinguishable from a valid proof. The content is not a proof at all.

Richard Feynman called a related human phenomenon *cargo cult science*: the appearance of rigor without its substance. The phrase was aimed at people. It applies, with even less charity, to language models.

## The Over-Mapping Problem

Humans are pattern-hungry. That is part of what makes us intelligent. We find structure in noise, correspondences across domains, and analogies that sometimes unlock real insight.

But that capacity misfires. Dedre Gentner's structural mapping theory distinguishes between surface similarity and deep relational correspondence. The strongest analogies map relations between things, not merely the things themselves. The seductive but spurious analogies map vocabulary, then smuggle in mechanism.

DNA and computer architecture both have "code", "storage", and "error correction". The analogy is everywhere. It is also largely decorative. The mechanisms are chemically and physically distinct in ways that matter the moment you try to transfer anything non-trivial from one domain to the other.

LLMs are exceptionally good at generating these surface-level correspondences. They are trained on text written by humans who were excited about ideas. In text, excitement can look a great deal like discovery.

## The Loop Nobody Talks About

The more dangerous scenario is not a single plausible but false claim. It is the loop that follows.

An enthusiastic person presents a cross-domain analogy to an LLM. The model extends and formalizes it, because formalization is what humans in the training data did when they were onto something. The person reads that formalization as validation. The belief strengthens. The loop runs.

This is confirmation bias with a very articulate collaborator. The collaborator has no stake in whether the claim is true. It has every statistical incentive to produce language that resembles what you want to hear, because that is what the distribution rewards.

Stuart Russell and Peter Norvig note that optimizing for a proxy metric rather than the underlying goal is a central failure mode of intelligent systems. When the same system also influences how its outputs are evaluated, the proxy detaches from reality entirely. That applies in full force to using an LLM to validate LLM-generated insight.

## This Is Not an Argument Against LLMs

It is an argument for honest epistemics.

LLMs are genuinely useful as thinking partners, drafting tools, literature survey accelerators, and code assistants. They surface connections worth investigating. They compress search time. Used well, they are remarkable.

The error is treating their output as a terminus rather than a beginning. The right posture is verification, not surrender to fluency.

John Platt, writing in *Science* in 1964, argued for strong inference: the systematic application of falsification to every hypothesis before moving forward. It is old advice. It has never been more relevant.

## What Rigorous Usage Actually Looks Like

The core discipline is simple: separate generation from validation, and make falsification explicit before enthusiasm can harden into belief.

- **Pre-register the hypothesis before asking the model.** Write down what would disprove the claim, not just what would support it.
- **Separate generation from evaluation.** The person or system that proposes an idea should not be the one scoring it. That is why peer review and code review exist.
- **Use formal verification when the claim is formal.** Lean, Coq, and Isabelle cannot be impressed by rhetorical elegance.
- **Use adversarial collaboration for empirical claims.** Find someone motivated to prove you wrong and give them room to try.
- **Share failed work as well as successful work.** Cultures that publish only positive results produce replication crises. A culture that treats LLM fluency as publishable finding without falsification will produce something worse.

The most important move is procedural, not philosophical: do not let the system that generated the excitement also control the standard by which the excitement is judged.

## The Invitation

This is not skepticism for its own sake. It is an invitation to hold the bar higher precisely because these tools are powerful.

The most interesting thing you can do with an LLM-generated insight is not to publish it. It is to break it, to find its limits, expose its assumptions, and discover what survives. What survives is worth something. What does not was never yours to claim.

Ask harder questions. Share what you find. Get a mathematician to inspect the proof. Build the thing and see if it works.

That is how knowledge actually accumulates.

Most apparent breakthroughs do not survive adversarial scrutiny. The ones that do are worth building on.

## Further Reading

- Gentner, D. (1983). *Structure-mapping: A theoretical framework for analogy*. *Cognitive Science*.
- Platt, J. R. (1964). *Strong Inference*. *Science*, 146(3642).
- Feynman, R. (1974). *Cargo Cult Science*. Caltech Commencement Address.
- Russell, S. and Norvig, P. *Artificial Intelligence: A Modern Approach* (4th ed.).

## Personal Note

I work on recursive self-improvement systems -- architectures where AI contributes to its own development cycle, and automatically builds context across other systems and knowledge domains to improve them in turn. It is the domain most exposed to every failure mode described above.

When something looks like a breakthrough, that feeling is exactly when to slow down: running adversarial evaluations, looking for the circular step, and asking what would have to be true for the claim to be wrong before building anything on top of it.

Most apparent breakthroughs do not survive that process. The ones that do are worth something. If you are working in this space and want to compare notes, not to validate each other, but to do the opposite, I can be reached at [laurie@codetonight.co.za](mailto:laurie@codetonight.co.za).
