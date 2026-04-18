---
title: The Harm Equation
slug: the-harm-equation
authors: [Public, Published, ACG Technical Committee, Commissioned by Alex Bunardzic]
publication_date: March 2026
doc_number: ACG-WP-002-2026
summary: Uncalibrated AI + Removed Humans + Commercial Incentive = Harm at Scale
status: published
site_href: the-harm-equation.html
---

A white paper on structural risk in AI-assisted engineering. The central claim is simple: the most damaging AI failures are not isolated bugs. They are the predictable output of a system that combines uncalibrated models, absent human judgment, and incentives that reward scale over care.

## Abstract

The rapid deployment of AI systems across industries has produced a recurring pattern of harm that is not random, not unpredictable, and not inevitable. This paper identifies and formalizes the structural equation that produces harm at scale in AI-assisted engineering.

> Uncalibrated AI + Removed Humans + Commercial Incentive = Harm at Scale

Each term is necessary but not sufficient. Remove any one term and the harm either does not occur, does not scale, or is caught before deployment. The equation requires all three variables to be active simultaneously.

This paper examines each variable, documents the mechanism by which they interact, and proposes the ACG Manifesto framework as the structural countermeasure.

This white paper is published by the AI Craftspeople Guild (ACG) as a reference document for engineering organizations, policymakers, educators, and individual practitioners seeking to understand why AI harm occurs at scale and what structural interventions prevent it.

## 1. Introduction

The AI industry in 2024-2026 has produced a specific and repeating failure pattern. Systems are deployed that generate incorrect medical advice, fabricate legal citations, produce discriminatory hiring decisions, amplify misinformation, and cause measurable psychological harm to users. These are not edge cases. They are the predictable output of a system operating exactly as the incentive structure demands.

The common response to each incident follows a script: surprise, apology, patch, and resumed operation. This response treats each failure as an isolated event, a bug to be fixed. This paper argues that the failures are not bugs. They are the structural output of a three-variable equation that the industry has, whether by negligence or design, allowed to become the default operating mode.

The equation is simple. Each variable is well-understood individually. The contribution of this paper is to formalize their interaction and demonstrate that the harm is a systems-level property that emerges only when all three variables are active simultaneously.

**Scope:** This paper addresses harm caused by AI systems in production environments serving real users. It does not address research, experimentation, or contained testing, where uncalibrated outputs are expected and appropriate. The distinction matters: a laboratory is not a deployment.

## 2. Term 1: Uncalibrated AI

### 2.1 Definition

An AI system is uncalibrated when the relationship between its confidence and its accuracy is unknown, unmeasured, or misrepresented. An uncalibrated system may produce outputs that are correct, incorrect, fabricated, or harmful, and neither the system nor its operators can reliably distinguish between these states before delivery.

### 2.2 Mechanisms of Miscalibration

**Hallucination without indication:** Large language models generate plausible text regardless of factual grounding. A model asked for legal citations will produce realistic-looking case numbers for cases that do not exist. The output format provides no signal that the content is fabricated.

**Distribution shift without detection:** A model trained on data from one domain, time period, or demographic is deployed on another. The model continues to produce outputs with the same apparent confidence, but accuracy degrades silently.

**Benchmark gaming without generalization:** Models are optimized for benchmark performance that does not transfer to production conditions. A model can score well on a standardized test and still fail badly on the organization's actual workload.

**Overfit to the evaluator:** When AI outputs are evaluated by other AI systems, calibration becomes circular. The evaluator shares the same failure modes as the generator, so shared errors become invisible.

### 2.3 Why Uncalibrated AI Alone Is Not Sufficient for Harm

Uncalibrated AI in a research lab, a sandboxed environment, or a system with human review at every output is a tool being used appropriately. The uncalibrated output is treated as a draft, a suggestion, or a starting point, never as a final product. Harm requires the next variable: the removal of the human who would catch the error.

**Analogy: the Mersenne boundary.** Every n-bit register has a maximum value of 2^n - 1. If you do not know the bit width, you do not know the boundary. An uncalibrated AI system is one where the bit width is unknown. You are writing values to a register without knowing when it overflows. The overflow is not malicious. It is structural.

## 3. Term 2: Removed Humans

### 3.1 Definition

Humans are removed when the verification, review, judgment, or override functions previously performed by human professionals are eliminated, bypassed, or reduced to a formality that cannot meaningfully catch errors before they reach end users.

### 3.2 Mechanisms of Removal

**Elimination for cost reduction:** The human reviewer is removed entirely. AI output flows directly to end users with no intermediate check.

**Dilution to ineffectiveness:** The human reviewer is retained but assigned a volume of AI outputs that makes meaningful review physically impossible.

**Deskilling through atrophy:** Over time, professionals who rely on AI for core judgments lose the expertise required to evaluate AI outputs.

**Authority inversion:** The human disagrees with the AI output but is overruled by organizational policy that treats the AI as authoritative.

### 3.3 Why Removed Humans Alone Is Not Sufficient for Harm

An organization with no human review of a well-calibrated, thoroughly tested AI system operating within documented boundaries may function acceptably for a period. The harm requires the specific combination of uncalibrated output and the absence of the human who would catch it. Without commercial incentive, there is also no structural reason to continue deploying the system once errors are discovered.

## 4. Term 3: Commercial Incentive

### 4.1 Definition

Commercial incentive, in the context of this equation, refers to the financial pressure to deploy AI systems faster, at larger scale, and at lower cost than the quality infrastructure can support. It is the force that makes uncalibration profitable and human removal attractive.

### 4.2 Mechanisms of Incentive-Driven Harm

**Speed-to-market over safety:** Testing, calibration, and human review are framed as competitive disadvantages. "We'll fix it in production" becomes policy when the cost of delay exceeds the expected cost of failure.

**Cost externalization:** The organization that deploys the AI system captures the revenue while users bear the cost of incorrect outputs. This asymmetry is the engine of the equation.

**Scale as a metric of success:** Venture capital, public markets, and corporate incentives reward users, transactions, and throughput. Quality is largely invisible in those metrics.

**Regulatory arbitrage:** Organizations deploy in jurisdictions or use cases where no specific AI regulation exists, treating the absence of prohibition as permission.

### 4.3 Why Commercial Incentive Alone Is Not Sufficient for Harm

Strong commercial incentive applied to a well-calibrated AI system with robust human oversight produces profitable products that work. Incentive becomes harmful only when it provides the motive to skip calibration and remove humans from meaningful review.

## 5. The Interaction: Why All Three Terms Are Required

The harm equation is multiplicative, not additive. Each term amplifies the others. Remove any single term and the equation collapses.

| Configuration | Outcome |
| --- | --- |
| Uncalibrated AI + Humans Present + Commercial Incentive | Humans catch errors before deployment. Harm is contained and the system improves through human feedback. |
| Calibrated AI + Removed Humans + Commercial Incentive | The system operates inside documented boundaries. Errors are rare and within expected tolerances. |
| Uncalibrated AI + Removed Humans + No Commercial Incentive | No pressure exists to deploy at scale. The system remains experimental, contained, or abandoned once errors are discovered. |
| **Uncalibrated AI + Removed Humans + Commercial Incentive** | **The harm equation. Errors are generated, not caught, and deployed at scale.** |

This is why isolated interventions fail. Improving model accuracy without restoring human review merely shifts the failure threshold. Adding a reviewer while preserving impossible review volume changes nothing. Regulation that can be delayed or gamed merely postpones harm.

## 6. Case Pattern Analysis

The following cases are documented not to single out specific organizations but to show that the equation produces consistent outcomes across industries.

### 6.1 Legal Citation Fabrication

**Term 1:** An LLM generates realistic but nonexistent legal citations.

**Term 2:** An attorney submits the brief without verifying citations against legal databases.

**Term 3:** Time pressure and cost reduction incentivize using AI for research that was previously done by humans.

**Outcome:** Court sanctions, professional discipline, and client harm.

### 6.2 Medical Misinformation at Scale

**Term 1:** A health-related chatbot generates plausible but incorrect guidance.

**Term 2:** No physician review exists between the model and patient-facing delivery.

**Term 3:** The deployer captures engagement and revenue from health-related queries.

**Outcome:** Incorrect dosage guidance, contraindication failures, and misdiagnosis suggestions at scale.

### 6.3 Discriminatory Hiring Automation

**Term 1:** Resume screening inherits demographic biases from historical data.

**Term 2:** Recruiters review only AI-approved candidates and never see the rejected pool.

**Term 3:** Automation reduces cost-per-hire, creating incentive to expand its use.

**Outcome:** Systematic exclusion of qualified candidates from protected classes.

### 6.4 The Common Structure

Every case follows the same structure: an AI system that does not know when it is wrong, a human who has been removed from the position where they would catch the error, and an economic engine that drives the erroneous output to the maximum number of affected people.

## 7. The ACG Manifesto as Structural Countermeasure

The six principles of the ACG Manifesto map directly to the three terms of the harm equation. Each principle disables or attenuates one or more terms.

| Manifesto Principle | Term Addressed | Mechanism |
| --- | --- | --- |
| 1. Embracing Innovation | Term 1 | Requires independent verification of AI capabilities and prevents adoption based on vendor claims alone. |
| 2. Demanding Quality | Term 1 + Term 2 | Mandates a verification harness for AI outputs and restores the human review gate. |
| 3. Ensuring Safety & Security | Term 1 + Term 3 | Requires threat modeling, operational boundaries, and visible liability. |
| 4. Protecting Humans | Term 2 + Term 3 | Centers human wellbeing over engagement and throughput metrics. |
| 5. Respecting User Agency | Term 2 | Ensures users know when AI is involved, restoring user agency as a distributed review layer. |
| 6. Right to Refuse | All three terms | Empowers the individual engineer to break the equation at any point. |

### 7.1 Principle 6 as the Master Switch

The Right and Duty to Refuse is the most important principle in the context of the harm equation because it is the only one that operates at the individual level. All other principles require organizational adoption. Principle 6 works even when the organization has failed: a single engineer who says "no, this is not ready" can break the equation regardless of what the organization wants.

This is why the ACG Technical Specification requires a protected ethical refusal register with no retaliation. The circuit breaker must be protected, or it will itself be removed.

## 8. The Scale Multiplier

The harm equation includes an implicit fourth variable that deserves explicit treatment: scale. The same three-term interaction that harms one user harms one million users with zero additional cost to the deployer.

**Industrial harm, pre-digital:** a defective physical product harms users proportional to units manufactured. Each defective unit has a marginal cost, so production capacity bounds the damage.

**AI harm, digital:** a defective AI output harms users proportional to deployment reach. The marginal cost of serving the next harmful output is effectively zero.

This is why the phrase "at scale" matters. Without scale, the harm equation describes a professional mistake. With scale, it describes a systemic crisis.

## 9. Structural Interventions

Effective interventions must be structural. They must alter the conditions that produce the equation rather than merely reacting to individual failures.

### 9.1 Calibration Requirements

- Mandatory calibration reporting for user-facing AI components.
- Domain-specific validation on the organization's actual workload.
- Continuous post-deployment calibration monitoring with defined suspension thresholds.

### 9.2 Human Restoration

- Human review volume that permits genuine evaluation.
- Maintenance of domain expertise independent of AI tooling.
- Preservation of human authority over AI outputs in disputed cases.
- Protected refusal rights for professionals who judge a system unsafe.

### 9.3 Incentive Alignment

- Liability internalization so deployers bear documented AI-originated harms.
- Quality metrics reported alongside scale and revenue metrics.
- Proactive engagement with regulation instead of exploiting regulatory gaps.

## 10. The Vetting Connection: ELIZA as Equation Breaker

The ACG's automated vetting service, ELIZA, is presented as a practical tool for assessing whether practitioners understand the harm equation and are prepared to act as circuit breakers. Its six-phase interview maps directly to the six manifesto principles and, by extension, to the three terms of the equation.

A practitioner who passes ELIZA's vetting has demonstrated that they can recognize when the AI is uncalibrated, when humans have been removed, and when commercial pressure is overriding safety. More importantly, they have demonstrated willingness to intervene.

**The reverse Turing test.** The original Turing test asks whether a machine can think like a human. ELIZA inverts this: is the human thinking at all? In the context of the harm equation, the critical question is not whether the AI is intelligent. It is whether the humans in the loop are conscious of the risks, conscious of their responsibility, and conscious of their power to refuse.

## 11. Conclusion

The harm produced by AI systems in production is not random, not mysterious, and not inevitable. It is the structural output of a three-variable equation:

> Uncalibrated AI + Removed Humans + Commercial Incentive = Harm at Scale

Each variable is necessary but not sufficient. Remove any one and the harm either does not occur, does not scale, or is caught before delivery. The equation is multiplicative: all three terms must be active simultaneously for harm to reach production at scale.

The ACG Manifesto provides the structural countermeasure. Its six principles map to the three terms and provide specific, actionable interventions at the organizational and individual level. The Technical Specification operationalizes these principles into auditable requirements with defined conformance levels. ELIZA provides individual-level vetting to ensure practitioners are conscious of the equation and prepared to break it.

The solution is not to stop using AI. The solution is to stop deploying AI under conditions where the harm equation is active.

Calibrate the AI. Keep the humans. Align the incentives. The equation breaks. The harm stops.

This is not idealism. This is engineering.

## 12. References

- ACG Manifesto, Rev. 1.0 (2026). AI Craftspeople Guild. https://aicraftspeopleguild.github.io/
- ACG-TS-001.1-2026. Technical Specification: Verification and Conformance Requirements for AI-Assisted Engineering Systems. AI Craftspeople Guild.
- ELIZA Automated Vetting Service. ACG Platform. Build specification, March 2026.
- ISA/IEC 62443 series. Industrial Automation and Control Systems Security.
- ISO/IEC 42001:2023. Artificial Intelligence - Management System.
- NIST AI Risk Management Framework 1.0 (2023).
- IEEE 7000-2021. Standard Model Process for Addressing Ethical Concerns During System Design.
- Weizenbaum, J. (1966). ELIZA - A Computer Program for the Study of Natural Language Communication Between Man and Machine. Communications of the ACM, 9(1), 36-45.
