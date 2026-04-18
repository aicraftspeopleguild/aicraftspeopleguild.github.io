---
title: The Prediction Trap
slug: the-prediction-trap
authors: [Public, Draft for Review, LC Scheepers and GRIP, Commissioned by Alex Bunardzic]
publication_date: March 2026
doc_number: ACG-WP-003-2026
summary: "When AI Diagnosis Cannot Be Wrong, It Cannot Be Right: A Popperian Analysis of Anticipatory AI in Healthcare"
status: published
site_href: the-prediction-trap.html
---

A Popperian analysis of anticipatory AI in healthcare. The paper argues that when an AI diagnostic claim cannot be falsified, it stops functioning as medicine and starts functioning as a commercial mechanism for expanding the patient pool.

## Abstract

A discussion in the AI Craftspeople Guild on 15 March 2026 surfaced a disturbing pattern: commercial entities are deploying AI-driven diagnostic tools that predict conditions in healthy populations, creating demand for treatment before clinical symptoms manifest.

> When AI diagnosis cannot be wrong, it cannot be right.

This paper examines the epistemological structure of these anticipatory AI systems through Karl Popper's falsification criterion and argues that the resulting Prediction Trap constitutes a novel category of harm that existing regulatory frameworks are not designed to address.

## 1. Introduction: A Conversation That Should Not Have Been Necessary

On 15 March 2026, a member of the AI Craftspeople Guild shared a commercial article predicting that artificial intelligence sleep apnea diagnosis would elevate care in 2026. The article projected 77 million US adults with obstructive sleep apnea by 2050 and marketed smartphone-based tappigraphy and AI-driven photoplethysmography as diagnostic tools without meaningful discussion of false positive rates, overdiagnosis risk, or the commercial interests of the entities making these projections.

The Guild's response was immediate and pointed. Thomas Frumkin, who had hours earlier published *The Harm Equation* (ACG-WP-002), recognized the pattern instantly: uncalibrated AI, absent human oversight, commercial incentive. Alex Bunardzic identified the broader trajectory: Western medicine progressed from being curative to preventative and now to anticipatory, where the system tells you that you will soon get something and should line up for screening before symptoms are even present.

That shift raises the real question. If the medical establishment is moving from treating what you have, to preventing what you might get, to predicting what you do not yet show, then the standard of evidence must become more rigorous at each step, not less.

Treating a broken leg requires an X-ray. Preventing a heart attack requires understanding risk factors across populations. Predicting disease in a healthy individual requires a level of specificity and calibration that no current AI system has demonstrated under deployment conditions.

Yet the commercial incentive runs in the opposite direction. The further upstream you move, from treatment to prediction, the larger the addressable market becomes. Everyone is a potential patient. This is not an accident of technology. It is the predictable result of deploying probabilistic classification systems inside a commercial healthcare infrastructure that rewards volume.

This paper examines that result through Karl Popper's falsifiability criterion and argues that the central question is not "is the AI accurate?" but "can the AI's prediction be shown to be wrong?" If it cannot, we are not practicing medicine. We are practicing something else entirely.

## 2. The Anticipatory Turn: From Cure to Prediction

The progression Bunardzic identified, curative, preventive, anticipatory, maps to a fundamental shift in the epistemic burden of proof.

**Curative medicine** operates on observable pathology. The patient presents with symptoms, the clinician identifies a condition, treatment is administered, and the outcome is measurable. The feedback loop is tight. Treatment either works or it does not. Falsification is built into the process.

**Preventive medicine** operates on population-level risk factors. Individuals are screened for markers that correlate with disease at the population level. The evidence base rests on longitudinal studies and randomized controlled trials. The epistemic burden is higher, but the methodology exists and the claims are testable.

**Anticipatory medicine**, the mode now being marketed by AI diagnostic companies, claims to identify disease in individuals before risk factors are clinically apparent. Smartphone sensors detect subtle patterns that supposedly predict conditions the individual does not yet have and may never develop. The epistemic burden is the highest of the three modes, yet the standard of evidence deployed is often the lowest: marketing copy, proprietary algorithms, and accuracy figures derived from internal validation sets that may not generalize to deployment populations.

This inversion, the highest epistemic burden paired with the lowest evidentiary standard, is the structural precondition for the Prediction Trap.

## 3. The Prediction Trap: Anatomy of a Feedback Loop

The Prediction Trap is a self-reinforcing cycle with four stages.

### Stage 1: AI Screening at Population Scale

An AI tool is deployed to screen a broad population: everyone with a smartphone, everyone wearing a fitness tracker, everyone who visits a commercial health website. The tool produces probabilistic assessments such as "You may be at risk for X."

### Stage 2: Overdiagnosis and Unnecessary Intervention

Some fraction of positive screens represents genuine pathology. A larger fraction represents false positives, incidental findings of uncertain significance, and conditions that would never progress to clinical disease. All positive screens, however, generate clinical activity: follow-up appointments, diagnostic tests, specialist referrals, prescriptions, and anxiety.

The evidence for this is not speculative. A Dutch study of approximately 19,000 participants using an AI skin cancer detection app found that app users had **twice as many biopsies and excisions**, benign skin tumor claims were **four times higher** at 5.9% versus 1.7%, and, paradoxically, app users had **fewer malignant lesion claims than controls**. Annual costs per app user were EUR 64.97 versus EUR 43.09 for the control-group non-users. The AI was not finding more cancer. It was finding more not-cancer and treating it as if it were.

### Stage 3: Revenue Generation and Reinvestment

Every clinical interaction generated by Stage 2 produces revenue for the healthcare system. Diagnostic tests, follow-up appointments, specialist consultations, and treatments are all billable events. The AI screening tool has created demand for services that would not otherwise have been rendered.

As *NPJ Digital Medicine* noted, AI devices pose a greater risk of overutilization than most medical devices and offer greater potential for fraud, waste, and abuse. When reimbursement is tied to use, overuse becomes financially rational.

### Stage 4: Expanded Screening Justified by Detection Rates

The revenue from Stage 3 funds expanded screening in Stage 1. The justification is always the same: more cases were detected that would otherwise have gone unnoticed. But detection without discrimination between progressive and non-progressive disease is not diagnosis. It is counting.

**The trap closes when detection rate becomes the success metric.** A screening program that finds more cases is deemed more successful regardless of whether those cases needed finding. The AI optimizes for sensitivity at the expense of specificity. This is Goodhart's Law applied to medicine: when the measure of success becomes the target, it ceases to be a good measure.

## 4. The Falsification Problem: What Would Prove the AI Wrong?

Karl Popper argued that a theory is scientific only if it is possible, in principle, to establish that it is false. A scientific system is tested by attempts to produce clashes between its claims and observation.

Apply that criterion to an AI system that predicts you may be at risk for sleep apnea based on your smartphone tap patterns.

If the prediction is "you are at high risk," and subsequent clinical testing reveals no sleep apnea, the AI company has two responses available. It can admit the system was wrong, which would degrade its reported accuracy and threaten the business model. Or it can retreat to the claim that the patient does not have it yet, that the AI detected pre-clinical patterns that may manifest later.

The second response is the one every commercial incentive points toward. If the prediction can never be disproven because it refers to a future that has not yet arrived, then it is not a medical prediction. It is, in Popper's terms, a conventionalist stratagem: a move designed to save the theory from falsification.

This is not hypothetical. It is the exact structure of anticipatory AI marketing. Claims about subtle patterns and increased predictive accuracy are made without published falsification conditions. If the company cannot say under what circumstances the AI would be judged wrong, then the accuracy claim is not a scientific statement. It is a commercial one.

### 4.1 The Popperian Test for AI Diagnostics

Any AI diagnostic claim that deserves to be taken seriously as medicine, rather than marketing, must answer three questions.

1. **What specific, measurable prediction does the AI make?** "You will develop clinically significant sleep apnea within 24 months" is testable. "You may be at risk" is not.
2. **What observation would prove this prediction wrong?** If no answer exists, the prediction is unfalsifiable.
3. **Has this falsification been attempted, and what were the results?** That means external validation on populations the AI was not trained on, published in peer-reviewed literature with disclosed conflicts of interest.

These are not unreasonable demands. They are the minimum standard for any medical intervention. The fact that most AI diagnostic companies cannot answer all three questions is itself the diagnosis.

## 5. The Evidence: What Happens When AI Predictions Meet Reality

### 5.1 The External Validation Gap

A systematic review of 86 deep learning algorithms for radiologic diagnosis found that **81% showed performance degradation on external validation**, with nearly a quarter showing substantial accuracy drops of 0.10 or more on a unit scale. Accuracy figures derived from internal test sets systematically overstate real-world performance.

The gap is not subtle. The Epic Sepsis Model, deployed across hundreds of US hospitals, demonstrated an AUC of 0.63 on external validation, and when predictions made after clinicians had already identified sepsis were excluded, the AUC dropped to **0.47, worse than a coin flip**. A later follow-up found only 15% sensitivity in real-world use.

This is not the failure of one model. It is a systematic property of the development-to-deployment pipeline. Proprietary performance claims do not reliably predict deployment performance.

### 5.2 The Automation Bias Amplifier

Even when AI predictions are presented as advisory, they alter human decision-making in ways that undermine oversight. Incorrect AI advice increased the risk of commission errors by **26%** compared with conditions that provided no decision support at all. Radiologists given AI explanations trusted AI diagnosis more quickly regardless of accuracy.

Task complexity and verification demands contribute to cognitive overload. When the cognitive load of verifying clinical AI advice exceeds working memory capacity, clinicians become more likely to over-rely on AI as a relief mechanism. The human-in-the-loop, in other words, is biased toward agreeing with the loop.

That creates a compounding problem. The AI generates a prediction, the clinician accepts it under time pressure and institutional signaling, and that acceptance is recorded as validation of the AI's quality. The feedback loop tightens.

### 5.3 The Regulatory Deficit

As of 2025, **96.4% of FDA-authorized AI medical devices** were cleared through the 510(k) pathway rather than the more rigorous PMA or De Novo pathways. In practice, most tools enter the market based on claims of substantial equivalence rather than demonstrated clinical benefit.

Globally, only **15.2% of countries** have enacted legally binding AI-specific legislation, and fewer than 10% have liability standards for AI in health. Regulation is not merely lagging deployment. It is absent from many of the decisions that matter.

An FDA-approved AI mammography algorithm was found to produce higher false positive rates for African-American women, older women, and women with denser breasts, generating nearly **three times more individual false-positive findings** than radiologists in some contexts. The clearance process did not catch the disparity. The patients did.

## 6. AI-trogenic Harm: A New Category

Ivan Illich, in *Medical Nemesis* (1975), identified three levels of iatrogenesis: clinical harm from treatments, social medicalization of life, and structural erosion of people's capacity to deal with health on their own terms. Fifty years later, that framework demands extension.

S. Tom de Kok has proposed a fourth category: **AI-trogenic harm**, harm that emerges from intertwined technological, institutional, and cultural factors where causation is opaque and attribution becomes nearly impossible. The Prediction Trap generates all four levels at once.

| Level | Mechanism in the Prediction Trap |
| --- | --- |
| Clinical | Unnecessary biopsies, procedures, and medications following false positive AI screens. |
| Social | Healthy individuals are reclassified as at risk on the basis of AI prediction and enter the patient role without clinical necessity. |
| Structural | Individuals lose confidence in their own bodily judgment and become dependent on algorithmic prompts to interpret health. |
| AI-trogenic | Harm emerges from the system as a whole. No single actor caused it, no single intervention stops it, and the loop resists correction because every participant benefits from continuation. |

The fourth level is the most dangerous because it has no single point of failure. The AI developer detects patterns. The clinician follows up on flagged results. The patient responds to information that appears authoritative. The insurer pays for documented activity. Every actor behaves reasonably within the role the system has assigned. The harm is an emergent property of the system.

## 7. The Moral Crumple Zone: Who Bears the Weight?

Madeleine Clare Elish's concept of the moral crumple zone describes how, in automated systems, a human actor with limited real control absorbs blame that protects the integrity of the technological system.

In the Prediction Trap, the moral crumple zone is the **general practitioner**. The GP receives the AI-screened patient, cannot dismiss the flagged result without accepting liability for a missed diagnosis, orders follow-up tests that generate their own false positives, and ultimately bears responsibility for the cascade that follows.

The AI developer is insulated because the algorithm performed as designed. The patient cannot be blamed for seeking care after being told they might be sick. The insurer paid for documented medical activity. The GP, the last human in the loop, crumples.

This is Frumkin's removed human viewed from the other end. The human is not absent, but stripped of meaningful agency. Present, but functionally decorative.

The pattern is familiar. When Uber's self-driving vehicle killed Elaine Herzberg in Tempe, Arizona, in March 2018, the company's safety architecture had already been reduced. The backup driver bore the charge. The organization that designed the conditions for complacency did not. The crumple zone absorbed the impact and the system rolled on.

## 8. The Exception That Proves the Rule

Intellectual honesty requires acknowledging that AI screening can work when the conditions are right. The MASAI trial in Sweden, a randomized controlled trial of AI-supported mammography screening, detected 20% more cancers with a 44% reduction in radiologist workload and no increase in false-positive rates.

But the MASAI trial is instructive precisely because of what it is *not*.

- It is **not autonomous**: AI triaged cases to single or double radiologist reading. No diagnosis was made without human assessment.
- It is **not anticipatory**: it screened for a condition with an established evidence base in a population already indicated for screening.
- It is **not commercially marketed to the general public**: it operated inside a national healthcare system with population-level accountability.
- It is **peer-reviewed and externally validated**: the results were published with full methodology disclosure.

The MASAI trial shows what AI-assisted screening looks like when the Prediction Trap is not operating. It is not the norm. It is the exception, and the distance between that exception and a smartphone app claiming to diagnose sleep apnea from tap patterns is the distance between medicine and marketing.

## 9. What Would Falsify This Thesis?

A paper that uses Popper's falsification criterion to indict AI diagnostics has to apply the same standard to itself. This thesis would be falsified by any of the following observations.

1. **A large-scale, independently validated study** showing that anticipatory AI screening reduces all-cause mortality or morbidity in the screened population compared with standard care after adjusting for lead-time bias and overdiagnosis.
2. **Evidence that commercial AI diagnostic companies systematically publish falsification conditions** alongside their accuracy claims, including the observations that would trigger withdrawal or material revision of the product.
3. **Evidence that the Prediction Trap feedback loop does not operate**, meaning AI screening does not increase downstream clinical activity, or that any increase produces net positive health outcomes.
4. **A regulatory framework that requires pre-market demonstration of net clinical benefit**, not just diagnostic accuracy on internal test sets, before AI screening tools can be marketed to the public.

The authors actively invite these falsifications. If the Prediction Trap is real, the evidence will continue to accumulate. If it is not, the evidence will show it. That is how science works. That is how medicine should work. That is how AI should be held to account.

## 10. Structural Countermeasures

### 10.1 Falsification as a Regulatory Requirement

No AI diagnostic tool should be marketed to the public without a published falsification protocol: a pre-registered statement of what observations would count as evidence that the tool does not work.

### 10.2 Net Benefit, Not Detection Rate

Regulatory approval and reimbursement should be tied to demonstrated net clinical benefit, reduced morbidity, reduced mortality, or improved quality of life, not simply to detection rates. A tool that detects more conditions but produces no improvement in outcomes should not be reimbursed.

### 10.3 Mandatory External Validation

Given that 81% of AI algorithms degrade on external validation, no AI diagnostic tool should receive market authorization based solely on internal validation. Independent external validation should be a minimum requirement.

### 10.4 The Human Gate

The lesson of the MASAI trial is that AI-assisted screening works when the human is not removed from the diagnostic decision. The human gate is not a concession to Luddism. It is a calibration mechanism that supplies domain knowledge, contextual judgment, and patient-specific assessment that the AI cannot provide.

### 10.5 Transparency of Commercial Interest

Every AI diagnostic tool marketed to the public should disclose the commercial relationship between the entity marketing the tool and the entities that profit from downstream clinical activity. When the company selling the screening tool also profits from treatment, the conflict of interest is structural, not theoretical.

## 11. Directions for Further Research

1. **Longitudinal overdiagnosis quantification:** What proportion of positive AI screens in direct-to-consumer health apps leads to clinical interventions that would not have occurred without the app?
2. **Falsifiability audit of commercial AI diagnostics:** Which tools publish falsification conditions, external validation results, and net clinical benefit data, and which do not?
3. **Automation bias in consumer settings:** Most automation bias research examines clinicians. The dynamics may be even worse when the audience is a layperson with high health anxiety.
4. **Economic modeling of the Prediction Trap:** What is the total economic cost, clinical, psychological, and societal, of the overdiagnosis cascade generated by direct-to-consumer AI screening?
5. **Regulatory effectiveness comparison:** As the EU AI Act, the FDA's evolving framework, and WHO guidance mature, how effective are they at preventing the Prediction Trap?
6. **Cultural iatrogenesis in the algorithmic age:** What happens to bodily autonomy when a generation grows up checking an app before deciding whether it feels well?

## 12. Conclusion

The Prediction Trap is not a conspiracy. It does not require malice, deception, or even negligence by any individual actor. It requires only three conditions that the current market provides in abundance: an AI system that makes predictions which cannot be falsified, a commercial infrastructure that profits from the downstream activity those predictions generate, and a regulatory environment that has not yet caught up to the epistemic shift from curative to anticipatory medicine.

Thomas Frumkin's *The Harm Equation* formalized the structure: uncalibrated AI + removed humans + commercial incentive = harm at scale. This paper identifies a specific instantiation of that equation in anticipatory healthcare and adds an epistemological dimension: the harm is compounded when the AI's predictions are structured to resist falsification.

A medicine that cannot be wrong cannot be right. A diagnostic tool that retreats to "you don't have it yet" when challenged is not practicing science. A commercial entity that profits from every positive screen while bearing no liability for false positives has no structural incentive to reduce them.

The commercial incentive does not self-correct. The regulatory framework does not yet exist. The patients do not know they are inside the trap.

The AI Craftspeople Guild exists because building AI systems is a craft and craft carries obligations to the people affected by what we build.

The countermeasure is not to reject AI in healthcare. It is to demand testable claims, falsifiable predictions, demonstrated net benefit, and human judgment at every point where a prediction becomes a decision about someone's body.

If we do not make that demand, no one else will.

> *The question that should keep you up at night is not whether AI will transform healthcare. It will. The question is simpler, and harder:*
>
> When an algorithm tells a healthy person they are sick, and no one in the system, not the developer, not the regulator, not the insurer, not the clinician, has either the incentive or the authority to say "no, you're not" ... who is the patient supposed to believe?

## References

- Bunardzic, A. (2026). AI Craftspeople Guild Manifesto, Rev. 1.0. <https://aicraftspeopleguild.github.io/>
- de Kok, S. T. (2025). "Iatrogenic to AI-trogenic Harm: Nonmaleficence in AI Healthcare." *Practical Ethics*, Uehiro Institute, University of Oxford. <https://blog.uehiro.ox.ac.uk/2025/02/guest-post-iatrogenic-to-ai-trogenic-harm-nonmaleficence-in-ai-healthcare/>
- Elish, M. C. (2019). "Moral Crumple Zones: Cautionary Tales in Human-Robot Interaction." *Engaging Science, Technology, and Society*, 5, pp. 40-60. <https://estsjournal.org/index.php/ests/article/view/260>
- Frumkin, T. (2026). *The Harm Equation* (ACG-WP-002-2026). AI Craftspeople Guild. <https://aicraftspeopleguild.github.io/guild/web/white-papers/the-harm-equation.html>
- Goddard, K., Roudsari, A., and Wyatt, J. C. (2012). "Automation bias: a systematic review of frequency, effect mediators, and mitigators." *Journal of the American Medical Informatics Association*, 19(1), pp. 121-127. <https://pmc.ncbi.nlm.nih.gov/articles/PMC3240751/>
- Illich, I. (1975). *Medical Nemesis: The Expropriation of Health*. Calder and Boyars.
- Lang, K. et al. (2023). "Artificial intelligence-supported screen reading versus standard double reading in the Mammography Screening with Artificial Intelligence trial (MASAI)." *The Lancet Oncology*, 24(8), pp. 936-944. <https://www.thelancet.com/journals/lanonc/article/PIIS1470-2045(23)00298-X/abstract>
- Lyell, D. and Coiera, E. (2017). "Automation bias and verification complexity: a systematic review." *Journal of the American Medical Informatics Association*, 24(2), pp. 423-431. <https://pmc.ncbi.nlm.nih.gov/articles/PMC7651899/>
- Obermeyer, Z. et al. (2019). "Dissecting racial bias in an algorithm used to manage the health of populations." *Science*, 366(6464), pp. 447-453. <https://www.science.org/doi/10.1126/science.aax2342>
- Popper, K. (1959). *The Logic of Scientific Discovery*. Routledge.
- RSNA (2024). "Incorrect AI Advice Influences Diagnostic Decisions." Radiological Society of North America. <https://www.rsna.org/media/press/i/2552>
- Sahni, N. R. et al. (2022). "Paying for artificial intelligence in medicine." *NPJ Digital Medicine*, 5, 63. <https://www.nature.com/articles/s41746-022-00609-6>
- SleepQuest (2026). "Sleep Apnea in 2026: 10 Key Predictions." <https://www.sleepquest.com/sleep-apnea-predictions/>
- Venkatesh, K. P., Raza, M., and Kvedar, J. (2023). "AI-based skin cancer detection: the balance between access and overutilisation." *NPJ Digital Medicine*. <https://pmc.ncbi.nlm.nih.gov/articles/PMC10427637/>
- Wong, A. et al. (2021). "External Validation of Deep Learning Algorithms for Radiologic Diagnosis: A Systematic Review." *Radiology: Artificial Intelligence*, 3(5). <https://pubs.rsna.org/doi/full/10.1148/ryai.210064>
- World Health Organization (2021). *Ethics and governance of artificial intelligence for health: WHO guidance*. <https://www.who.int/publications/i/item/9789240029200>
- World Health Organization (2023). "WHO outlines considerations for regulation of artificial intelligence for health." <https://www.who.int/news/item/19-10-2023-who-outlines-considerations-for-regulation-of-artificial-intelligence-for-health>
- Wu, E. et al. (2023). "FDA-cleared artificial intelligence and machine learning-based medical devices and their 510(k) predicate networks." *The Lancet Digital Health*, 6(2), e123-e130. <https://www.thelancet.com/journals/landig/article/PIIS2589-7500(23)00126-7/fulltext>
