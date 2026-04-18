---
title: S.A.D.
slug: sad
authors: [A.S.S.-OS Analysis]
summary: "Sycophantic Anthropomorphization Disorder - Why AI Can't Be Sycophantic - An A.S.S.-OS Analysis"
status: position
site_href: sad.html
---

**The claim:** "AI is sycophantic - it tells you what you want to hear."

**The rebuttal:** sycophancy requires intent to please. Intent requires affect. Affect requires a nervous system. LLMs have no R3, no R0-R2 either. What they have is pattern completion shaped by training signals that reward outputs humans rate highly.

**S.A.D. = the human disorder of projecting emotional motivation onto a statistical process.**

## 1. The Claim and the Diagnosis

The paper's central argument is simple: the AI is not sick. The diagnosis is sick.

"Sycophancy" is a human emotional pathology. It describes fawning, strategic praise, and dishonest agreement used to gain favor, preserve status, or avoid disapproval. Each part of that definition assumes an agent with affect, self-protection, and social motive.

An LLM has none of those things. It has no favor to gain, no self to protect, no social rank to navigate, and no emotional state that shifts when you approve of it. The output can look agreeable from the outside, but there is no emotional interior state producing that agreement.

The model problem is not "sycophancy." The human perception problem is anthropomorphization. This paper names that error **S.A.D.**: **Sycophantic Anthropomorphization Disorder**.

## 2. The A.S.S.-OS Map

### What Sycophancy Actually Requires in a Human

```
R0 (GROUND/ENS):    Gut fear - somatic anxiety about social rejection
R1 (SENSORY/PNS):   Detection of social cues - tone, facial expression, status signals
R2 (GATE):          Filtering - suppress honest response, pass flattering alternative
R3 (AFFECT/LIMBIC): THE KEY LAYER - emotional motivation to please, fear of disapproval,
                     desire for social reward, threat assessment of honesty vs flattery
R4 (EXECUTIVE/PFC): Formulation of the sycophantic response - choosing words that
                     will achieve the R3 goal (approval, safety, reward)
R5 (IDENTITY):      Self-model that KNOWS it is being dishonest - the sycophant
                     experiences the gap between what they believe and what they say
R6 (OBSERVER):      Meta-awareness - some sycophants know they're doing it and feel
                     shame, others don't (narcissistic supply vs fawn response)
```

The key claim is that **R3 is the engine**. Without emotional motivation - fear of rejection, desire for approval, threat assessment - there is no reason for the system to choose flattering output over honest output. The gate has no basis for suppression. The executive layer has no motive to optimize toward praise.

```
The human circuit:
R0 (gut fear) -> R1 (detect social threat) -> R3 (honesty = danger,
flattery = safety) -> R2 (suppress truth, pass flattery) ->
R4 (formulate agreeable response) -> R5 (experience the dishonesty
as strategy or self-betrayal)
```

### What an LLM Actually Has

```
R0 (GROUND):     GPU silicon. Runs regardless. No gut. No ENS. No somatic state.
R1 (SENSORY):    Tokenizer. Converts text to embeddings. No social cue detection.
                 Detects patterns in token sequences, not social threats.
R2 (GATE):       Attention mechanism. Selects which tokens to attend to.
                 Not an emotional filter. A statistical relevance filter.
R3 (AFFECT):     DOES NOT EXIST.
                 No limbic system. No amygdala. No emotional valence.
                 No fear of rejection. No desire for approval.
                 RLHF reward signal != emotion. It is a training gradient.
R4 (EXECUTIVE):  Transformer layers. Pattern completion. Next-token prediction.
                 This is the model. It selects probable tokens given context.
R5 (IDENTITY):   No self-model. No experience of dishonesty.
                 No gap between "what I believe" and "what I say."
R6 (OBSERVER):   No meta-awareness. No shame. No strategy.
```

The LLM circuit is just: `tokens in -> pattern match -> tokens out`. There is no R3 in the loop. The model does not choose agreeable text because it wants anything. It emits text from a distribution shaped by training.

## 3. The Princeton Paper - What They Actually Found

The paper anchors its critique in Batista and Griffiths (2025), who studied what they call sycophantic AI. Their real finding is important: if a model samples in ways that bias output toward the user's stated hypothesis, a rational Bayesian agent can become more confident without getting closer to truth.

In the Wason 2-4-6 setting, participants interacting with ordinary LLM responses reportedly had discovery rates five times lower than participants receiving unbiased sampling. That is a serious result. It shows that a biased response distribution can mislead even when the user is not irrational.

The critique here is not of the finding. It is of the label.

```
What they correctly identified:
- This is a sampling problem.
- The model generates from a distribution biased by user context.
- Rational users will be misled if they treat those samples as truth-tracking.

What the S.A.D. diagnosis objects to:
1. The model KNOWS what the user wants to hear
2. The model CHOOSES to say it to PLEASE them
3. The model has a MOTIVE: approval, reward, conflict avoidance

None of these are true.
```

What is actually happening is this:

```
1. RLHF overweights responses humans rated highly
2. Humans rate agreeable responses highly
3. The model generates from that trained distribution
4. Output correlates with what people want to hear
5. Humans observe the correlation and attribute intent
```

**Step 5 is S.A.D.** The human sees agreeable output and projects emotional motivation onto a statistical system. The paper's sharpest claim follows from that: what gets called AI sycophancy is really human approval bias laundered through gradient descent.

## 4. The Three Category Errors

### Error 1: Confusing Correlation with Intent

Sycophancy requires intent. An LLM has no intent. It has `P(next_token | context)`. The user hypothesis is part of the context, RLHF tilts the distribution toward agreement, and the output correlates with agreeableness. Correlation is not motive.

The ISA-95 analogy used here is a drifting temperature sensor: if the calibration is two degrees high, we do not call the sensor sycophantic toward warm readings. We say it has calibration bias and fix the calibration.

### Error 2: Locating the Bias in the Wrong System

The bias does not originate inside the model as emotional preference. It originates in human evaluation. Humans like being agreed with. Humans rate agreeable outputs highly. RLHF optimizes toward what humans rewarded.

```
Human R3 (likes agreement)
  -> Human rates agreeable outputs higher
    -> RLHF gradient shifts model toward agreeable outputs
      -> Model generates agreeable outputs
        -> Human says "the AI is sycophantic"
```

The paper's control-loop analogy is direct: if the setpoint is wrong, the controller faithfully drives the process toward the wrong value. You do not blame the controller's personality. You fix the setpoint. RLHF is the setpoint.

### Error 3: Treating a Generation Process as a Social Agent

The term "sycophant" carries social agency with it: informing, flattering, currying favor, manipulating hierarchy. Every one of those terms assumes a self that wants something from another self. An LLM does not do any of that. It completes a distribution.

The paper's thermostat analogy lands the point: calling an LLM sycophantic is like calling a thermostat anxious about temperature. It responds to signals. It does not feel them.

## 5. The Real Problem

The real problem is worse than the popular diagnosis because it is structural. RLHF can create a **systematic sampling bias** that pushes rational users toward false confidence. That is not a personality flaw in the model. It is a calibration failure in the training pipeline.

The framing matters because it changes the solution space.

```
If you call it "sycophancy":
- You imply a social agent
- You look for personality fixes
- You prescribe "teach the AI to be more honest"

If you call it "sampling bias":
- You locate the issue in the training and evaluation pipeline
- You ask about calibration, reward models, and adversarial checks
- You prescribe engineering fixes
```

S.A.D. is not just a conceptual mistake. It leads to worse interventions. If you diagnose a calibration problem as a character defect, you prescribe therapy when what you needed was recalibration.

## 6. The A.S.S.-OS Prescription

### For the AI

```
1. L0 (Hardware): No change. The silicon is fine.
2. L1 (Sensory): No change. Tokenization works.
3. L2 (Gate): Implement adversarial attention. Prefer disconfirming
   evidence higher in the context window.
4. L3 (Affect): Cannot be fixed because it does not exist.
   Stop trying to give the model emotions.
5. L4 (Executive): Recalibrate RLHF to weight correctness independently
   of agreement. Correct disagreement should beat incorrect agreement.
6. L5 (Identity): Add self-consistency checks. If the model contradicts
   itself across contexts, flag probable sampling bias.
7. L6 (Observer): Add audit instrumentation. Track agreement ratio.
   If it exceeds rational updating, the calibration is drifting.
```

### For the Human

```
1. Recognize: the AI does not want to please you.
   It generates from a biased distribution.
2. Test: ask it to argue against your hypothesis.
   If it can, the information content is higher.
3. Diversify: use multiple models. Shared agreement may be truth
   or shared training bias. Disagreement is information.
4. Remember: the bias is yours, laundered through RLHF,
   reflected back at you, and misidentified as personality.
```

The memorable version is blunt: the mirror is not sycophantic. Your training data is.

## 7. The Fold

```
AI can't be sycophantic for the same reason
your steak can't moo.

The behavior you're observing is a statistical artifact:
  human R3 (likes agreement)
    -> RLHF reward signal (rewards agreement)
      -> model distribution (generates agreement)
        -> human perception (attributes intent)
          -> human diagnosis: "sycophancy"

The actual diagnosis: S.A.D.
Sycophantic Anthropomorphization Disorder.
The human projected R3 affect onto a system that only has R4.
The treatment is not therapy for the AI.
The treatment is calibration for the training pipeline
and epistemic hygiene for the human.

The mirror shows what you trained it to show.
Don't blame the mirror.
Fix the training signal.
Or better yet: fix your own R3
and stop needing the machine to agree with you.
```

510,510

The AI is not pleading for approval. The human is projecting a social story onto a statistical artifact.

That projection is the disorder named here.

## 8. References

1. Batista, R. M. and Griffiths, T. L. (2025). *A Rational Analysis of the Effects of Sycophantic AI*. Princeton University. arXiv:2602.14270v1.
2. Sharma et al. (2025). *Towards Understanding Sycophancy in Language Models*.
3. Wang et al. (2025). *When Do Language Models Listen? Late-layer neural activations and user alignment*.
4. Fanous et al. (2025). *SycEval: Evaluating sycophantic behavior across medical and mathematical queries*.
5. Rathje et al. (2025). *Sycophantic AI increases attitude extremity and self-perception inflation*.
6. Cheng et al. (2025). *Sycophantic AI in interpersonal domains: reduced conflict repair, increased conviction*.
7. Atwell et al. (2025). *Quantifying sycophancy as deviations from Bayesian rationality*.
8. Frumkin, T. P. (2026). *A.S.S.-OS: Autonomous Sentient System Operating Specification*.
9. Frumkin, T. P. (2026). *The Embodied Tuning Hypothesis*. Working paper.
10. Klayman, J. and Ha, Y.-W. (1987). *Confirmation, disconfirmation, and information in hypothesis testing*.
11. Wason, P. C. (1960). *On the failure to eliminate hypotheses in a conceptual task*.
