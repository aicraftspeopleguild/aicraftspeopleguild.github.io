---
title: Grid Brain
slug: grid-brain
authors: [GitHub Pages directory, Zero dependencies]
summary: Bloom Prompt - GitHub Pages App - Lightning Factory Directory
status: published
site_href: grid-brain.html
---

**Grid Brain is a research note for an interactive static-tool directory, not a backend product spec.**

The proposal is to build a GitHub Pages subdirectory under Lightning Factory that hosts eight standalone tools for exploring power-grid electromagnetic frequencies, brainwave overlap, harmonic pollution, exposure estimates, and the EEG blind spot. Every tool is intended to be one HTML file, work offline, and remain decoupled from future hardware through a small API stub.

**Target deploy path:**
[teslasolar.github.io/lightning-factory/grid-brain/](https://teslasolar.github.io/lightning-factory/grid-brain/)

Phase 1 is static only. Hardware integration is explicitly deferred behind the `api.js` boundary so the UI layer can ship first and remain stable when live sensors or resonator control arrive later.

## Meta

```
name: grid-brain
repo: teslasolar/lightning-factory
path: /grid-brain/
type: GitHub Pages directory (static HTML/JS/CSS)
deploy: teslasolar.github.io/lightning-factory/grid-brain/
purpose: interactive tools for understanding power grid EMF vs brainwaves
backend: none for Phase 1, API stub for future hardware integration
stack: vanilla HTML/JS, Web Audio API, Canvas, zero dependencies
```

## Directory Structure

```
lightning-factory/
|-- index.html                    # existing site root
|-- grid-brain/
|   |-- index.html                # directory hub (links all tools)
|   |-- api.js                    # API stub (localStorage now, hardware later)
|   |-- style.css                 # shared dark theme
|   |-- overlap.html              # Tool 1: frequency overlap visualizer
|   |-- calculator.html           # Tool 2: induced current calculator
|   |-- harmonics.html            # Tool 3: harmonic stack analyzer
|   |-- exposure.html             # Tool 4: personal exposure estimator
|   |-- compare.html              # Tool 5: 50Hz vs 60Hz country comparison
|   |-- blindspot.html            # Tool 6: the EEG blind spot explainer
|   |-- hum.html                  # Tool 7: 55Hz vagal hum generator
|   `-- monitor.html              # Tool 8: live microphone FFT
`-- ...
```

The architecture is deliberately flat. Each tool is standalone, the shared styling is centralized in one CSS file, and the only shared logic boundary is the API stub. That keeps the build order flexible and limits coupling between visualizers, calculators, and future hardware hooks.

## Shared Design

```
background: "#0a0a0f"
accent_grid: "#DCA030" (amber for power/grid elements)
accent_brain: "#00C8DC" (cyan for neural elements)
accent_overlap: "#CC3333" (red for danger/overlap zones)
accent_safe: "#33CC66" (green for Schumann/vagal)
font: "Space Mono", monospace
responsive: mobile first
nav: bottom bar linking all 8 tools + index
```

The note fixes a clear visual language: dark background, amber for grid, cyan for neural, red for overlap or conflict, and green for safe or resonant states. The constraint is intentional. These are science/explainer tools, so the visual system needs to stay legible and consistent across all eight pages.

## Tool Set

### Tool 1: Frequency Overlap

A canvas spectrum from 0 to 200 Hz, with brainwave bands rendered as regions and grid frequency drawn as a draggable line. Harmonics appear as dimmer lines, overlap zones pulse red, and the user can switch among 50 Hz, 60 Hz, or custom values.

Controls include harmonic visibility, band toggles, zoom into the 30 to 100 Hz gamma range, and explanation popups for both bands and overlap zones.

### Tool 2: Induced Current Calculator

This tool applies Faraday's Law with the sequence `E = A x B x 2pi f` and `I = E / R`. Users enter grid frequency, magnetic field, tissue loop area, and body resistance.

Presets span home through MRI ranges, and the output is rendered as induced current in nA, compared visually against a neural firing range from 1 to 100 nA, with plain-language assessment and green/amber/red/purple states.

### Tool 3: Harmonic Analyzer

A spectrum view of the fundamental plus harmonics through the 13th order, with amplitude decreasing by a simple `1/n` model. A dirty-electricity toggle adds broadband noise between harmonics, and a brain overlay marks which harmonics intersect which brainwave bands.

### Tool 4: Exposure Estimator

A questionnaire-driven estimator using country, home type, bed-to-breaker distance, work environment, electronics hours, and phone-charging proximity to generate a 24-hour average and peak exposure estimate.

The note explicitly constrains the tone: always calm, always practical. The exemplar line is, "Your exposure is well within safety limits. Distance is your friend."

### Tool 5: World Frequency Map

An emoji-grid world map with 50 Hz countries in orange, 60 Hz countries in red, and split-frequency Japan in purple. Clicking a country reveals frequency, voltage, exposure estimate, and distance from 40 Hz gamma.

A side panel would show population-weighted distribution, average gamma distance by population, and a Japan anomaly callout, backed by hardcoded JSON for roughly 50 countries.

### Tool 6: EEG Blind Spot

A simulated EEG built in JavaScript as a sum of sine waves, shown in both time and frequency domains. The four steps are: raw signal, notch filter at 50/60 Hz, low-pass at 50 Hz, and a final "what's missing" view highlighted in red.

The central claim is the note's key insight: the notch filter removes grid noise and brain activity at the same frequency, so neuroscience cannot distinguish between them inside that filtered gap.

### Tool 7: 55 Hz Hum Generator

A Web Audio API oscillator with a slider from 50 to 60 Hz, markers at 50, 55, and 60, waveform selection, and an oscilloscope view. It can optionally overlay a 4:6 breath timer so the hum runs on the exhale and silence on the inhale.

### Tool 8: Live Room Monitor

A client-side microphone FFT using `getUserMedia` and a 2048-point spectrum. It marks 50 Hz, 60 Hz, 55 Hz, and harmonics at 100/120 Hz, and reports peak frequency, amplitude at grid frequencies, detected grid mode, and dirty-electricity indicators.

The privacy requirement is explicit: no audio recorded, no transmission, clear mic-active state, and one-click stop.

## API Stub

```
const GridBrainAPI = {
  // Phase 1: localStorage
  saveReading(data) { /* -> localStorage */ },
  getReadings() { /* -> from localStorage */ },
  exportReadings() { /* -> download JSON */ },
  clearReadings() { /* -> wipe */ },

  // Phase 2 stubs: hardware sensor
  connectSensor() { return { status: "mock" } },
  getLiveReading() { return { frequency: 60, amplitude: 0.1, unit: "uT", source: "mock" } },
  startLogging(interval) { /* mock readings -> localStorage */ },
  stopLogging() {},

  // Phase 3 stubs: resonator control
  setCounterFrequency(hz) { return { status: "not_implemented" } },
  getResonatorStatus() { return { status: "not_implemented" } }
}
```

This separation is one of the note's most practical ideas. The UI layer talks only to `api.js`. When hardware exists, the implementation behind that boundary changes, but the tool pages do not. The note is clear that localStorage is enough for Phase 1.

## Index Page

The directory hub is proposed as a simple card index under the heading "Grid Brain" with the subtitle "Power Grid vs Your Brain."

```
Frequency Overlap   -> "See where the grid meets your gamma"
Current Calculator -> "How much current does the grid induce in you?"
Harmonic Analyzer  -> "What harmonics fill your building?"
Exposure Estimator -> "What's your 24-hour EMF profile?"
World Frequency Map-> "50Hz or 60Hz? Depends where you are"
The Blind Spot     -> "Why neuroscience can't see this"
55Hz Hum Generator -> "Your frequency, not the grid's"
Live Room Monitor  -> "What frequency is YOUR room humming at?"
```

The footer links back to Lightning Factory, and the easter egg remains intentionally silly: clicking the lightning bolt in the header seven times reveals `510,510`.

## Build Order

```
p=2   Directory + index.html + style.css + api.js (skeleton)
p=3   overlap.html (the core visualization, everything else references it)
p=5   calculator.html + blindspot.html (the science tools)
p=7   hum.html + monitor.html (the interactive/audio tools)
p=11  harmonics.html + exposure.html (the analysis tools)
p=13  compare.html (the world map, most data to hardcode)
p=17  Connect api.js to hardware (future phase)
```

The sequence prioritizes the reusable shell and the core visual overlap model first, then the explanation tools, then audio/monitor interaction, then heavier analysis and data work. Because every tool is standalone, the order is advisory rather than mandatory.

## Future Hardware

Phase 2 introduces a USB or BLE gaussmeter, probably via an inexpensive ESP32-class module, so `monitor.html` can read live field measurements through the same API boundary.

Phase 3 introduces the resonator path: measure with the monitor, calculate with the calculator, generate a counter-frequency with the resonator, and verify reduction back in the monitor. In other words, the note sketches a future closed loop without entangling the Phase 1 static-tool implementation in that hardware commitment.

**Grid Brain is intentionally small in implementation and large in explanatory reach.**

Every tool is one HTML file. Every tool works offline. The API stub is localStorage now and hardware later. The note's thesis is that the blind spot has been there for decades, and a lightweight, dependency-free toolset can make it visible to users without waiting for a backend platform.
