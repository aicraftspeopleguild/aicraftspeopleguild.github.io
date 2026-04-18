---
title: Lightning Factory
slug: lightning-factory
authors: [Feasibility Study, Experimental Protocols, Engineering Specifications, KONOMI Project]
publication_date: March 2026
summary: Schumann Resonance Cognitive Enhancement System
status: published
site_href: lightning-factory.html
---

**The guild is labeling this document as experimental on purpose.**

Lightning Factory is presented here as a feasibility study and protocol proposal, not as a validated medical or productivity intervention. The engineering stack is concrete, the study design is specific, and the hypothesis is testable, but the claimed cognitive benefits remain unproven pending controlled trials.

**Experimental rubric:** this paper describes a speculative system, explicit validation criteria, and stop conditions. It is meant to be read as a research and engineering proposal with built-in no-go gates, not as settled guidance.

## Table of Contents

1. [Executive Summary](#executive)
2. [Scientific Foundation](#foundation)
3. [Experimental Protocols](#protocols)
4. [Hardware Specifications](#hardware)
5. [Safety and Regulatory](#safety)
6. [Implementation Roadmap](#roadmap)
7. [References](#references)

## 1. Executive Summary

### The Hypothesis

Global lightning activity, roughly 100 strikes per second, generates continuous ELF electromagnetic fields at 7.83 Hz and harmonics. Human brainwave bands occupy overlapping frequency ranges. The proposal is that artificial replication of these fields in workspaces may enhance cognitive performance.

### The Opportunity

The paper argues that no rigorous double-blind workplace productivity studies currently exist for this class of intervention, which makes the first validated study outcome commercially and scientifically valuable.

### Bottom Line

| Metric | Assessment |
| --- | --- |
| Technical feasibility | Trivial in principle. The proposed hardware stack already exists in adjacent domains. |
| Safety profile | Projected operating range remains well below cited exposure limits. |
| Scientific plausibility | Suggestive, not proven. The evidence base is correlational and mixed. |
| Commercial viability | Unknown until controlled study outcomes are available. |
| Regulatory pathway | Presented as a wellness-device path with no disease claims. |

## 2. Scientific Foundation

### 2.1 The Natural System

```
EARTH-IONOSPHERE CAVITY
============================================================

    Ionosphere (~100 km)
    ========================================================
         ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^
         Standing waves at 7.83 Hz + harmonics
         ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^

    Lightning strikes: ~100/sec globally

    ========================================================
    Earth surface (conductor)

RESONANT FREQUENCIES:
- f1 = 7.83 Hz   (fundamental)
- f2 = 14.3 Hz   (2nd harmonic)
- f3 = 20.8 Hz   (3rd harmonic)
- f4 = 27.3 Hz   (4th harmonic)
- f5 = 33.8 Hz   (5th harmonic)
- f6 = 39.0 Hz   (6th harmonic)

FIELD CHARACTERISTICS:
- Magnetic field: ~1 picoTesla (10^-12 T)
- Electric field: ~0.1 mV/m
- Energy density: ~10^-7 J/s*m^3
- Global, continuous, omnipresent
```

### 2.2 Human Brainwave Correspondence

```
FREQUENCY ALIGNMENT
============================================================

Hz:  0    5    10   15   20   25   30   35   40
     |    |    |    |    |    |    |    |    |

SR:       v         v         v         v    v
         7.83     14.3      20.8      27.3  33.8

EEG: |====DELTA====|
              |====THETA====|
                   |=====ALPHA=====|
                        |========BETA========|
                                    |===GAMMA===|

FUNCTIONAL MAPPING:
- 7.83 Hz  <-> Theta (creativity, meditation, insight)
- 14.3 Hz  <-> Alpha (relaxed focus, learning)
- 20.8 Hz  <-> Beta  (active thinking, problem-solving)
- 27.3 Hz  <-> Beta  (concentration)
- 33.8 Hz  <-> Gamma (peak cognition, binding)
```

### 2.3 Existing Evidence Summary

| Study | Finding | Strength |
| --- | --- | --- |
| Persinger 2012 | Real-time EEG-Schumann coherence | Peer-reviewed, replicated |
| Saroka and Persinger 2015 | Spectral power density correlation | Peer-reviewed |
| Cherry 2003 | Evolutionary brain-Schumann tuning hypothesis | Theoretical |
| PEMF cardiac studies | 7.83 Hz associated with protection against oxidative stress | Multiple replications |
| Grounding and earthing studies | EEG alpha increase within milliseconds | Moderate quality |
| Ion exposure studies | Negative ions associated with relaxed alpha states | Mixed results |

**Gap:** the paper identifies the absence of controlled workplace productivity studies as the main open question.

## 3. Experimental Protocols

### 3.1 Study 1: Acute Cognitive Effects (Lab)

#### Design: Randomized Double-Blind Crossover

```
PROTOCOL SCHEMATIC
============================================================

Participants: N=60 healthy adults
Power target: d=0.5, alpha=0.05, beta=0.80

Screening     Baseline      Condition A     Washout     Condition B
    |            |              |              |              |
    v            v              v              v              v
[Health] -> [Cognitive] -> [60 min exp.] -> [7 days] -> [60 min exp.]
[EEG cap]   [EEG rest]     [+ tests]                      [+ tests]

ACTIVE condition:
- 7.83 Hz + harmonics
- 1-10 uT

SHAM condition:
- Device on
- 0 field

Randomization:
- Counterbalanced
- Half get active first, half sham first

Blinding:
- Participants blinded
- Testers blinded
```

#### Outcome Measures

```
PRIMARY OUTCOMES (COGNITIVE BATTERY)
============================================================
- Working memory
  - N-back task (2-back, 3-back)
  - Metrics: accuracy %, reaction time (ms)

- Attention
  - Continuous Performance Test (CPT)
  - Metrics: d' sensitivity, commission errors

- Executive function
  - Trail Making Test (A and B)
  - Metrics: completion time (s), errors

- Processing speed
  - Symbol Digit Modalities Test
  - Metric: correct responses in 90s

- Creativity
  - Alternate Uses Task
  - Metrics: fluency, flexibility, originality

SECONDARY OUTCOMES (PHYSIOLOGICAL)
============================================================
- EEG
  - Power spectral density
  - Coherence with applied field
  - Alpha peak frequency shift

- Heart rate variability
  - RMSSD, SDNN
  - LF/HF ratio

- Salivary cortisol
  - Pre/post exposure samples

- Subjective
  - Alertness, focus, mood
  - NASA Task Load Index
```

#### Statistical Analysis Plan

```
ANALYSIS PIPELINE
============================================================

1. Primary analysis
   Mixed-effects model:
   Y = b0 + b1(Condition) + b2(Order) + b3(Period) + u_i + e

2. Multiple comparison correction
   Benjamini-Hochberg FDR (q < 0.05)

3. Effect size reporting
   Cohen's d with 95% CI

4. Responder analysis
   Identify subgroups by baseline physiology

5. EEG-behavior correlation
   Test whether Delta alpha predicts Delta cognition
```

### 3.2 Study 2: Chronic Workplace Effects (Field)

#### Design: Cluster-Randomized Controlled Trial

```
PROTOCOL SCHEMATIC
============================================================

Site selection: 8 comparable open-plan offices
Randomization: 4 active, 4 sham
Duration: 12 weeks

Week 0          Weeks 1-12              Week 12
  |                 |                      |
  v                 v                      v
[Baseline] --> [Intervention period] --> [Follow-up]

ACTIVE offices:
- Continuous system operation
- 8am-6pm weekdays

SHAM offices:
- Same visible hardware
- 0 field output

Blinding:
- Participants told only "environmental optimization system"
- Managers blinded to assignment
- Data collectors blinded to assignment
```

#### Outcome Measures

```
PRIMARY OUTCOMES (PRODUCTIVITY)
============================================================
- Objective work output
  - Lines of code / commits
  - Documents completed
  - Tickets closed
  - Revenue generated, if applicable

- Error rates
  - Existing quality metrics

- Meeting efficiency
  - Decisions per meeting-hour

SECONDARY OUTCOMES
============================================================
- Monthly cognitive subset
  - N-back
  - Symbol Digit

- Weekly wellbeing surveys
  - WHO-5
  - PSS-4
  - Pittsburgh Sleep Quality Index

- Physiological subset (n=40)
  - Wearable HRV
  - Morning salivary cortisol

- Sick days
- Turnover intent
```

#### Power Analysis

```
SAMPLE SIZE CALCULATION
============================================================

Assumptions:
- Minimum detectable effect: 8% productivity increase
- ICC: 0.05
- Average cluster size: 25 employees
- Design effect: 1 + (25 - 1)(0.05) = 2.2
- Alpha: 0.05
- Power: 0.80

Calculation:
- Effective sample size per arm: 100 / 2.2 ~= 45
- Clusters needed per arm: 45 / 25 ~= 2
- With dropout buffer: 4 clusters per arm
- Total: 8 offices, about 200 participants
```

### 3.3 Study 3: Dose-Response Characterization

#### Design: Within-Subjects Parametric Study

| Condition | Frequency | Field Strength | Note |
| --- | --- | --- | --- |
| SHAM | None | 0 uT | Control |
| LOW-7.83 | 7.83 Hz only | 1 uT | Low-dose active |
| MED-7.83 | 7.83 Hz only | 10 uT | Mid-dose active |
| HIGH-7.83 | 7.83 Hz only | 100 uT | High-dose active |
| HARMONICS | 7.83 + 14.3 + 20.8 | 10 uT each | Composite active |
| MISMATCH | 11 Hz | 10 uT | Specificity control |

This study is designed to answer whether there is a genuine dose-response relationship, whether 7.83 Hz is specifically important relative to any ELF signal, whether harmonics add benefit, and where an optimal field strength might sit.

## 4. Hardware Specifications

### 4.1 System Architecture

```
LIGHTNING FACTORY SYSTEM v1.0
============================================================

+---------------------------------------------------------+
|                    CONTROL UNIT                         |
|  +-------------+  +-------------+  +-----------------+ |
|  | Waveform    |  | Amplifier   |  | Monitoring and  | |
|  | Generator   |->| Stage       |->| Logging         | |
|  | (DSP)       |  | (Class D)   |  | (uC + WiFi)     | |
|  +-------------+  +-------------+  +-----------------+ |
+-------------------------+-------------------------------+
                          |
              +-----------+-----------+
              |                       |
        +-----v-----+           +-----v-----+
        | Coil Array|           | Coil Array|
        |  North    |           |  South    |
        +-----------+           +-----------+
              |                       |
              +-----------+-----------+
                          |
                          v
                +-----------------------+
                |    Workspace Volume   |
                | Uniform field         |
                | 1-100 uT @ 7.83 Hz    |
                | + harmonics           |
                +-----------------------+
```

### 4.2 Component Specifications

```
WAVEFORM GENERATOR
============================================================
- Type: Direct Digital Synthesis (DDS)
- Frequency resolution: 0.01 Hz
- Frequency range: 0.1 - 100 Hz
- Waveform: Sinusoidal (THD < 0.1%)
- Channels: 6
- Phase control: 0-360 degrees per channel
- Output: 0-5V analog

AMPLIFIER
============================================================
- Type: Class D
- Efficiency: > 90%
- Power: 50W per channel
- Current: 0-10A per coil
- Protection: overcurrent, thermal, short

COIL ARRAY (PER UNIT)
============================================================
- Type: Helmholtz-like configuration
- Wire: 14 AWG enameled copper
- Turns: 200 per coil
- Diameter: 1.5 m
- Spacing: 0.75 m
- Inductance: about 50 mH
- Resistance: about 2 ohms
- Field uniformity: +/-5% over 2m^3 volume
- Mounting: ceiling or floor

FIELD STRENGTH TARGETS
============================================================
- Minimum effective: 1 uT
- Typical operating: 10 uT
- Maximum: 100 uT
- Earth's DC field: about 50 uT
- Safety limit target: < 400 uT

MONITORING SUBSYSTEM
============================================================
- Magnetometer: 3-axis fluxgate
  - Range: +/-200 uT
  - Resolution: 0.01 uT
  - Bandwidth: DC-100 Hz
- Microcontroller: ESP32
- Logging: local SD + cloud upload
- Alerts: field deviation, coil fault
- API: REST interface
```

### 4.3 Installation Configurations

```
CONFIGURATION A: SINGLE WORKSTATION
============================================================
                    +-----+
                    |Coil |
                    | 1m  |
                    +--+--+
                       |
          +------------+------------+
          |                         |
          |      Workstation        |
          |   Field zone 2x2x2 m    |
          |                         |
          +------------+------------+
                       |
                    +--+--+
                    |Coil |
                    +-----+

Cost: about $500
Coverage: 1 person
Power: 10W

CONFIGURATION B: OPEN OFFICE
============================================================
Ceiling grid + floor grid
3m spacing
Coverage: about 200 m^2
Cost: about $8,000
Power: 200W
Coils: 8 ceiling + 8 floor

CONFIGURATION C: CONFERENCE ROOM
============================================================
Single ceiling coil + floor or table coil
Coverage: 8-12 people
Cost: about $1,500
Power: 30W
```

### 4.4 Waveform Specification

| Frequency (Hz) | Amplitude | Phase | Purpose |
| --- | --- | --- | --- |
| 7.83 | 1.000 | 0 deg | Fundamental / theta |
| 14.30 | 0.600 | 30 deg | 2nd harmonic / alpha |
| 20.80 | 0.400 | 60 deg | 3rd harmonic / beta |
| 27.30 | 0.250 | 90 deg | 4th harmonic |
| 33.80 | 0.150 | 120 deg | 5th harmonic / gamma |
| 39.00 | 0.100 | 150 deg | 6th harmonic |

```
Composite waveform:
B(t) = B0 * sum_i A_i * sin(2pi * f_i * t + phi_i)

Where B0 is the base field strength (1-100 uT)
and the fundamental period is about 127.7 ms.
```

## 5. Safety and Regulatory

### 5.1 Exposure Limits

```
COMPARISON TO SAFETY STANDARDS
============================================================

Field strength comparison (uT):

0.001    0.01     0.1      1       10      100     1000
  |        |        |       |        |        |        |
  |        |        |       |        |========|        |  Lightning Factory range
  |        |        |       |        |        |        |
  |        |        |       |        |        |--------|  ICNIRP occupational
  |        |        |       |        |--------|          ICNIRP public
  |        |        |-------|                               PEMF therapy typical
  |--------|                                                Earth DC field ~50 uT

Operating margin claimed:
- 100x to 1000x below occupational limits
```

### 5.2 Regulatory Pathway

```
REGULATORY CLASSIFICATION
============================================================

United States (FDA):
- Proposed classification: general wellness device
- Not a medical device if no disease claims are made
- No premarket submission required under that framing
- Suggested labeling: "supports relaxation and focus"

European Union (CE):
- Low Voltage Directive
- EMC Directive
- Not a medical device under MDR if no medical claims
- Self-declaration with technical file

Claims the paper says can be made:
- Supports relaxation
- Promotes focus
- Simulates natural Earth frequencies
- Environmental optimization

Claims the paper says cannot be made:
- Treats any condition
- Cures anything
- Improves cognition without qualification
- Any disease-related claim
```

### 5.3 Contraindications and Warnings

```
CONTRAINDICATIONS
============================================================
- Implanted electronic devices
  - Pacemakers
  - Defibrillators
  - Insulin pumps
  - Cochlear implants

- Pregnancy (precautionary)
- Epilepsy or seizure disorders (theoretical entrainment risk)

WARNINGS
============================================================
- Not a substitute for medical treatment
- Discontinue if any adverse symptoms
- Keep away from magnetic storage media
- May interfere with sensitive instruments
```

## 6. Implementation Roadmap

### 6.1 Phase Timeline

```
PROJECT TIMELINE
============================================================

Year 1                          Year 2                    Year 3
Q1   Q2   Q3   Q4              Q1   Q2   Q3   Q4         Q1   Q2
|    |    |    |               |    |    |    |          |    |
v    v    v    v               v    v    v    v          v    v

[Phase 1]
- Hardware development
- Lab prototype
- IRB approval

[Phase 2]
- Lab study (n=60)
- Dose-response study
- Data analysis

[Phase 3]
- Field study (n=200)
- 8 offices over 12 weeks

[Phase 4]
- Product launch

Milestones:
- M1: Working prototype
- M2: IRB approval
- M3: Lab study published
- M4: Field study complete
- M5: Commercial product ready
- M6: First commercial installation
```

### 6.2 Budget Estimate

| Phase | Key Costs | Subtotal |
| --- | --- | --- |
| Phase 1: Hardware Development | Prototyping, coil fabrication, test equipment, engineering labor | $135,000 |
| Phase 2: Lab Study | EEG equipment, participant compensation, lab overhead, research staff, statistics | $152,000 |
| Phase 3: Field Study | Office installations, wearables, research staff, coordination, analysis | $187,000 |
| Phase 4: Commercialization | Industrial design, manufacturing setup, certification, inventory, launch | $175,000 |
| **Total Project Budget** | Estimated end-to-end program cost | **$649,000** |

### 6.3 Go/No-Go Decision Criteria

```
DECISION GATES
============================================================

After Phase 2, proceed to field study if:
- At least 2 cognitive measures show p < 0.05
- Effect size d > 0.3 on a primary outcome
- No adverse events are reported
- There is a clear dose-response or frequency-specific signal

Pivot if:
- There are physiological effects but no cognitive effects
- Reframe toward wellness or stress reduction only

Terminate if:
- No significant effects appear on any measure
- 7.83 Hz performs the same as mismatch frequency
- Sham performs equal to or better than active

After Phase 3, proceed to commercialization if:
- Productivity increase is at least 5%
- Or wellbeing improves by at least 0.5 SD
- Customer ROI is positive
- No adverse pattern appears
```

## 7. References

### Primary Scientific Literature

1. Persinger, M.A. (2012). Brain electromagnetic activity and lightning: potentially congruent scale-invariant quantitative properties. *Frontiers in Integrative Neuroscience*, 6, 19. <https://pmc.ncbi.nlm.nih.gov/articles/PMC3351789/>
2. Saroka, K.S. and Persinger, M.A. (2015). Human Quantitative EEG and Schumann Resonance Exhibit Real-Time Coherence. *Journal of Signal and Information Processing*, 6, 153-164. <https://www.scirp.org/journal/paperinformation?paperid=56609>
3. Cherry, N.J. (2003). Human intelligence: the brain, an electromagnetic system synchronised by the Schumann Resonance signal. *Medical Hypotheses*, 60(6), 843-844. <https://pubmed.ncbi.nlm.nih.gov/12699709/>
4. Price, C. (2016). ELF Electromagnetic Waves from Lightning: The Schumann Resonances. *Atmosphere*, 7(9), 116. <https://www.mdpi.com/2073-4433/7/9/116>
5. Price, C. and Williams, E. (2020). Natural ELF fields in the atmosphere and in living organisms. *International Journal of Biometeorology*. <https://link.springer.com/article/10.1007/s00484-020-01864-6>
6. McCraty, R. et al. (2017). Synchronization of Human Autonomic Nervous System Rhythms with Geomagnetic Activity. *IJERPH*, 14(7), 770. <https://pmc.ncbi.nlm.nih.gov/articles/PMC5551208/>

### Safety Standards

7. ICNIRP (2010). Guidelines for Limiting Exposure to Time-Varying Electric and Magnetic Fields (1 Hz - 100 kHz). *Health Physics*, 99(6), 818-836.
8. IEEE C95.6 (2002). Standard for Safety Levels with Respect to Human Exposure to Electromagnetic Fields, 0-3 kHz.

### Supplementary Reviews

9. Youvan, D.C. (2024). Brain Waves and the Schumann Resonance: Exploring the Electromagnetic Connection. *ResearchGate*. <https://www.researchgate.net/publication/384040884>
10. Schumann Resonances and Human Bioregulation. *Bioregulatory Medicine Institute*. <https://www.brmi.online/post/2019/09/20/schumann-resonances-and-their-effect-on-human-bioregulation>

## Appendix A: Bill of Materials (Prototype)

| Qty | Component | Supplier | Unit $ | Total $ |
| --- | --- | --- | --- | --- |
| 1 | ESP32 DevKit | Espressif | 10 | 10 |
| 1 | AD9833 DDS Module | Analog Devices | 15 | 15 |
| 1 | TPA3116 Class D Amp (2ch) | TI | 25 | 25 |
| 2 | 14 AWG magnet wire (500 ft) | Remington | 80 | 160 |
| 2 | Coil former (1.5 m hoop) | Custom | 50 | 100 |
| 1 | 24V 10A Power Supply | Mean Well | 40 | 40 |
| 1 | HMC5883L Magnetometer | Honeywell | 12 | 12 |
| 1 | SD Card Module | Generic | 5 | 5 |
| 1 | Enclosure | Hammond | 30 | 30 |
| - | Connectors, wire, misc | Various | 50 | 50 |
| **Total** | | | | **$447** |

## Appendix B: Firmware Pseudocode

```
// LIGHTNING_FACTORY_v1.0
// Schumann resonance generator firmware

#define F1  7.83
#define F2  14.30
#define F3  20.80
#define F4  27.30
#define F5  33.80
#define F6  39.00

float amplitudes[] = {1.0, 0.6, 0.4, 0.25, 0.15, 0.10};
float phases[]     = {0, 30, 60, 90, 120, 150};

void setup() {
    init_dds();
    init_amplifier();
    init_magnetometer();
    init_wifi();
    init_logging();

    set_field_strength(10.0);  // uT
    set_frequencies({F1, F2, F3, F4, F5, F6});
    set_amplitudes(amplitudes);
    set_phases(phases);
}

void loop() {
    update_dds_output();

    float measured_field = read_magnetometer();

    if (abs(measured_field - target_field) > 0.1) {
        adjust_amplifier_gain();
    }

    if (millis() - last_log > 1000) {
        log_to_sd(timestamp, measured_field, target_field);
        upload_to_cloud();
        last_log = millis();
    }

    if (wifi_command_available()) {
        process_command();
    }
}
```

**Notice:** this document describes experimental technology.

The cognitive enhancement effects of artificial Schumann resonance exposure are hypothetical and require validation through the proposed studies. This page is not medical advice, and the document itself already specifies the no-go conditions under which the project should stop.
