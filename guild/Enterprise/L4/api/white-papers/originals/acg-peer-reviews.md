---
title: ACG Review Forge
slug: acg-peer-reviews
authors: [Peer Review, AI Evaluation, Gamified Progression]
summary: Bloom Prompt - Gamified Peer Review + AI Evaluation System
status: published
site_href: acg-peer-reviews.html
---

**Make reviewing as rewarding as publishing.**

The Guild charter says peer reviews are mandatory, but peer review is usually invisible labor. Publishing gets recognition. Reviewing gets silence. This document reframes review as a first-class guild activity with visible progression, measurable skill, feedback loops, and earned status for the reviewer as well as the author.

The core move is simple: make the review itself a quantified artifact. Every stage produces data. Every data point feeds progression, recognition, queue management, and charter-aligned evaluation.

## The Review Lifecycle

```
SUBMIT    author submits work to guild
ASSIGN    system matches reviewers by skill and domain
REVIEW    reviewer evaluates against rubric
SCORE     review produces structured assessment
REVISE    author responds to review
ACCEPT    work passes review threshold
REWARD    both author and reviewer earn points
```

The lifecycle is deliberately explicit. The proposal treats each stage as a data-producing event so review can be tracked, improved, and made visible across the network.

## Review Rubric

```
DIMENSION          WHAT IT MEASURES                    WEIGHT
----------------------------------------------------------------
Accuracy           Are claims factually correct?         20%
Evidence           Are claims supported by evidence?     20%
Novelty            Does this add something new?          15%
Reproducibility    Can someone else do this?             15%
Clarity            Is it understandable?                 10%
Ethics             Does it align with charter values?    10%
Practicality       Can it be applied in the real world?  10%
----------------------------------------------------------------
TOTAL                                                     100%
```

Each dimension is scored from 1 to 5. The overall result is a weighted score out of 5.0. Acceptance requires a minimum total of 3.5 and no single dimension below 2.0.

Reviewers must provide a written justification for each score. One line minimum. The author sees the justifications, either anonymized or named at the reviewer's choice.

### Submission Categories

```
CATEGORY              DESCRIPTION                          REVIEW MIN
---------------------------------------------------------------------------
Research              Original research, analysis, study    3 reviewers
Specification         Technical spec, standard, protocol    2 reviewers
Tool                  Software tool, app, utility           2 reviewers
Position Paper        Opinion, policy recommendation        2 reviewers
Tutorial              Educational content, how-to guide     1 reviewer
Case Study            Real-world application report         2 reviewers
Ethical Review        Refusal report, harm analysis         3 reviewers
AI Evaluation         Testing an AI claim or product        2 reviewers
```

AI Evaluation is treated as a charter-core category. The paper breaks it into claim testing, tool comparison, risk assessment, adoption reporting, and failure analysis.

## Reviewer Skill System

### Reviewer Tiers

```
TIER   NAME         REQUIREMENT                         BADGE
--------------------------------------------------------------
R0     Apprentice   Guild member (any)                 [checklist]
R1     Reviewer     3 completed reviews                [lens]
R2     Trusted      10 reviews + quality > 3.5        [book]
R3     Senior       25 reviews + domain depth         [target]
R4     Lead         50 reviews + mentored 3           [scales]
R5     Master       100 reviews + 5 domains           [hall]
```

### Review Quality Score

```
After the author receives a review, they rate:
- Was the review helpful?        (1-5)
- Was the feedback specific?     (1-5)
- Was the tone constructive?     (1-5)
- Did it improve the work?       (1-5)
```

The average becomes the Review Quality Score, or RQS. Volume alone is not enough. A reviewer who produces vague, unhelpful feedback does not advance.

### Domain Expertise Tags

```
DOMAIN TAGS
- ai-safety          - architecture        - security
- data-science       - automation          - healthcare
- finance            - industrial          - ethics
- education          - research-methods    - nlp
- creative           - blockchain          - iot
```

Tags are self-declared at first and then earned through repeated review work. The paper proposes awarding a domain tag after three reviewed submissions in that area and using those tags for reviewer-submission matching.

### Author Progression

```
TIER   NAME           REQUIREMENT                         BADGE
---------------------------------------------------------------
A0     Contributor    1 submission (any status)          [pencil]
A1     Published      1 accepted submission              [page]
A2     Established    5 accepted submissions             [stack]
A3     Prolific       15 accepted + 3 categories         [trophy]
A4     Distinguished  30 accepted + high impact          [star]
A5     Fellow         50 accepted + mentored 5           [medal]
```

## Point System

### Earning Points

```
ACTION                                    POINTS    NOTES
----------------------------------------------------------------
Submit for review                           10      any category
Pass review (accepted)                      50      per submission
Pass review first round (no revision)      +25      bonus
Complete a review                           30      per review completed
Review quality > 4.0                       +15      bonus
Review quality > 4.5                       +10      additional bonus
Revise based on feedback                    15      responsiveness
Review an ethical refusal                   50      hardest review type
Mentor a new reviewer                       40      per mentored reviewer
Submit AI evaluation                        20      charter core function
AI evaluation accepted                      75      highest publication value
Recruit member who publishes                25      network growth
Serve as lead reviewer                      40      assign + oversee
```

### Activity and Decay

Points do not expire, but activity still matters. Members with no review or submission activity in 90 days are flagged as dormant and removed from the active leaderboard until they return.

### The 510,510 Cap

The proposal caps total available points across the guild at 510,510. As activity grows, the relative value of each point adjusts, echoing the KCC token logic and the A.S.S.-OS fold.

## Achievements

### Review Achievements

```
ACHIEVEMENT         RARITY      TRIGGER
---------------------------------------------------------------
First Review        common      Complete 1 review
Helpful Critic      common      RQS > 4.0 on 3 reviews
Speed Reader        uncommon    Complete review within 48 hours
Deep Dive           uncommon    Review > 2000 words
Cross Domain        uncommon    Review in 3 different domains
Quality Control     rare        RQS > 4.5 on 10 reviews
Gatekeep            rare        Correctly reject 3 submissions
The Mentor          rare        Mentor 3 new reviewers to R1
Iron Reviewer       epic        50 reviews, RQS > 4.0
The Standard        epic        100 reviews, all domains
Founding Reviewer   legendary   Reviewed in the first month
```

### Author Achievements

```
ACHIEVEMENT         RARITY      TRIGGER
---------------------------------------------------------------
First Blood         common      Submit anything
Clean Shot          uncommon    Accepted first round, no revision
Polymath            uncommon    Accepted in 3+ categories
AI Auditor          rare        5 accepted AI evaluations
Harm Spotter        rare        Published AI risk assessment later validated
The Spec            rare        Published spec adopted by 3+ members
Peer Magnet         epic        Submission attracted 5+ reviewers
Fellow              legendary   50 accepted submissions
```

### Dual Achievements

```
ACHIEVEMENT         RARITY      TRIGGER
---------------------------------------------------------------
Both Sides          uncommon    10 reviews and 5 publications
The Cycle           rare        Reviewed work that cited your work
Renaissance         epic        R3+ reviewer and A3+ author
The Guild           legendary   All of the above + mentored + recruited
```

## Leaderboards and Anti-Gaming

### Active Leaderboards

```
BOARD             METRIC                   REFRESH
--------------------------------------------------------
Top Reviewers     Review count + RQS      Weekly
Top Authors       Accepted + score        Weekly
Most Helpful      RQS ranking             Monthly
Domain Leaders    Per domain tag          Monthly
Speed Reviewers   Average review time     Monthly
Overall           Combined points         Monthly
Rising            Most improved           Monthly
```

### Anti-Gaming Rules

```
RULE                                      WHY
-------------------------------------------------------------------
Min review length 200 words               No drive-by reviews
Min 3 dimensions scored per review        No blanket approvals
Self-review impossible                    Obvious
Review swapping detected and flagged      Catch reciprocal gaming
Rejection must be justified               No gatekeeping by fiat
Author can appeal rejection               Keeps reviewers honest
Appeal reviewed by lead reviewer          Not the original reviewer
```

## Integration with ACG-NET

```
manifest.json additions:
  member.stats.reviews_completed: int
  member.stats.review_quality_avg: float
  member.stats.submissions_total: int
  member.stats.submissions_accepted: int
  member.stats.reviewer_tier: "R0"-"R5"
  member.stats.author_tier: "A0"-"A5"
  member.stats.domains: ["ai-safety", "automation", ...]
  member.achievements: [...existing + review achievements]

brain_tier_integration:
  Review activity  -> counts toward R2 ring
  Publishing       -> counts toward R1 ring
  AI evaluation    -> counts toward R6 ring
  Ethical review   -> counts toward R3 ring

hub_display:
  Review activity on member profile
  Review queue on hub dashboard
  "Needs Reviewers" section on hub index
  Domain-matched reviewer suggestions
```

The paper's most important integration rule is that upper-tier brain rankings require both review and publication. You cannot reach the highest guild tiers by only shipping or only judging. The system is designed to reward members who do both.

### The Review Queue

```
display:
  Submissions awaiting review, sorted by:
  - Age (oldest first)
  - Category (AI evaluations highlighted)
  - Reviewer match

submission card:
  - Title + category + author
  - Required reviewers: X of Y assigned
  - Domain tags needed
  - "Claim this review" button

reviewer can:
  - Browse queue and claim reviews
  - Get auto-matched suggestions
  - Set availability

author can:
  - Track review status
  - See which reviews are complete
  - Respond to individual reviews
  - Resubmit revised version
```

## Implementation

```
phase_1_manual:
  Reviews happen in GitHub issues or markdown files
  Scoring is self-reported in structured template
  Points tracked in JSON in the hub repo
  Leaderboard computed by hub GitHub Action

review_template.md:
  Submission: [title]
  Reviewer: [handle]
  Date: [date]
  Scores:
    Accuracy: [1-5] - [justification]
    Evidence: [1-5] - [justification]
    Novelty: [1-5] - [justification]
    Reproducibility: [1-5] - [justification]
    Clarity: [1-5] - [justification]
    Ethics: [1-5] - [justification]
    Practicality: [1-5] - [justification]
  Overall: [weighted average]
  Recommendation: [accept / revise / reject]
  Summary: [paragraph]

phase_2_app:
  GitHub Pages app for review submission and tracking
  Form-based review submission
  Auto-computed scores
  Dashboard with leaderboards
  Notifications when reviews are needed
  Lives at: guild hub site /reviews/

phase_3_chain:
  Reviews recorded on ACG-KCC chain
  Review hashes as immutable proof
  Reviewer reputation on-chain
  Achievement NFTs as non-transferable proof of contribution
```

## The Charter Connection

```
CHARTER SAYS:                      SYSTEM PROVIDES:
-------------------------------------------------------------------
"peer reviews are mandatory"      -> structured review process
"scientific approach"             -> 7-dimension rubric with scoring
"evaluated by real effects"       -> reproducibility + practicality
"not novelty alone"               -> novelty is only 15% of score
"experimentation and learning"    -> AI evaluation category
"approached with discernment"     -> ethics dimension on every review
"tested in practice"              -> case study category
"judged by real effects"          -> impact tracking over time
```

The gamification is not decorative. The document's thesis is that the charter becomes real when its principles are instrumented. Review, scoring, progression, appeals, and visible contributions are the system by which the guild turns values into enforceable practice.

**Reviewing is as valuable as publishing. The system makes that visible.**

The points make it real. The tiers make it progressive. The achievements make it fun. The charter already said peer review is mandatory; Review Forge makes peer review desirable, legible, and measurable.
