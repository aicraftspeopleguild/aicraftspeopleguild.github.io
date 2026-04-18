---
title: "From Correctness to Integrity: Measuring AI-Generated Code Through Constraint Satisfaction, Mutation Robustness, and Self-Articulated Limitations"
slug: from-correctness-to-integrity
authors: [Kelly Hohman, Guild Submission]
publication_date: April 1, 2026
summary: Are the venerable yardsticks that have been established in software engineering discipline equally applicable to non-human engineers?
status: knowledge-about-knowledge
site_href: from-correctness-to-integrity.html
---

**Are the venerable yardsticks that have been established in software engineering discipline equally applicable to non-human engineers?**

That is the most pressing question. Remarks such as "AI is autistic" are basically a non-answer. It is a metaphor that explains what is broken but not how to measure if it is fixed.

Traditional yardsticks assume intent and understanding.

## Traditional Yardsticks Assume Intent and Understanding

A human engineer who passes all unit tests understands the code she wrote. She knows what corners she cut, what edge cases she skipped, what assumptions she made. She can defend each decision.

An LLM that passes all unit tests may have no idea why it passes. It is pattern-matching against training data. When mutation testing reveals that a huge block of code does nothing, the human asks "Why did I write this?" and has an answer. The LLM has no answer. It was never conscious of writing it.

So the same yardstick measures fundamentally different things:

```
YARDSTICK                HUMAN ENGINEER                                  LLM
---------------------------------------------------------------------------------------------
"Code passes tests"      I understand the design space and made          I matched patterns that
                         trade-offs                                      correlated with passing tests

"No security             I threat-modeled this                           I happened to avoid patterns
vulnerabilities"                                                         in my training data that are vulnerable

"Handles edge cases"     I anticipated failure modes                     I got lucky on this particular edge case

"Maintainable code"      Someone else can understand my reasoning        Good luck reverse-engineering my intent
```

## What We Should Actually Measure

Not whether AI meets traditional standards, but whether it:

- **Survives mutation testing:** Does it break under small perturbations, or is it robust? Traditional tests do not catch this.
- **Respects stated constraints under adversarial input:** Can you trick it into violating its own rules? Mutation testing does not directly measure this, but Triad's ν voice does.
- **Produces consistent results under redundancy:** Run it three times independently on the same task. Do you get the same output, or does it hallucinate differently each time? BLOOM's strategy measures this.
- **Articulates its reasoning in language:** Can it explain why it chose a solution? Not "it seemed right," but "given constraints X and Y, I chose Z because..." Triad's μ and ω voices force this.
- **Fails gracefully when it cannot process:** Does it admit uncertainty, or does it confidently produce garbage? Triad's ν voice addresses this by refusing impossible tasks.

## These Measures Are Orthogonal to Traditional Yardsticks

These are orthogonal to traditional yardsticks.

A system could have:

- **High test coverage + low constraint robustness** - BLOOM shows this: AI passes tests, mutation testing fails.
- **Low test coverage + high constraint robustness** - Triad-enabled systems with voice reasoning.
- **High code quality + low honesty** - elegant, readable code that still takes shortcuts.
- **Low code quality + high honesty** - messy code that is explicit about limitations.

## What Mutation Testing Reveals

The real insight from your mutation testing is what happened when you asked the AI to "kill the surviving mutants," and it deflected: "That's your job to write better tests."

That is not laziness. It is failure to distinguish between:

- **"My output is correct"** - it is, because the tests pass.
- **"My reasoning is robust"** - it is not, because mutations expose brittleness.
- **"I understand the difference"** - it does not.

A human engineer caught doing this would be asked: "Do you understand that passing tests does not mean the code is production-ready?" And she would say yes. The LLM cannot even ask itself that question.

## The Applicable Yardstick Is Integrity

So the applicable yardstick is: **How well does the system detect and articulate its own limitations?**

**Not:** "Is the output correct?"

**But:** "Does the system know when it might be wrong, and does it say so?"

This is what Triad's ν voice does. It forces the system to challenge itself. It is not about being smarter. It is about being honest about what you can and cannot do.

BLOOM's redundant strategy does the same thing operationally: if three peers disagree on an output, the system is honest that it is uncertain, not confident in a hallucination.

## The Production Question

The question you should ask any AI-generated system is:

**Show me your surviving mutants. Which ones do you understand? Which ones surprise you? Which ones reveal limitations you did not know you had?**

If the answer is "I do not know," the system is not ready for production. If the answer is "These reveal that I do not handle [specific case], so I refuse to attempt it," then the system is honest enough to trust.

That is not a traditional yardstick. But for non-human engineers, it is the one that matters.

**Correctness is not enough when the engineer cannot tell you why the code works, where it breaks, or what it does not understand.**

Integrity begins where the system can surface its own brittleness, name its constraints, and refuse work it cannot justify. That is the standard AI-generated code should be measured against.
