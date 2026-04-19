# AI Craftspeople Guild — Test Harness

This document describes the test harness set up to ensure that any new deployment does not break the existing site at [aicraftspeopleguild.github.io](https://aicraftspeopleguild.github.io).

---

## Overview

The test suite is composed of three layers:

| Layer | File | Tool | Purpose |
|---|---|---|---|
| Unit | `tests/unit.spec.js` | Vitest + node-html-parser | Validate HTML structure without a browser |
| Functional | `tests/functional.spec.js` | Playwright | Verify every known page loads and behaves correctly |
| Visual regression | `tests/visual.spec.js` | Playwright | Detect unintended visual changes via screenshot diff |

---

## Non-Regression Logic

The non-regression logic is now clear:

- **Page deleted** → test fails (404)
- **Page renamed** → test fails (404 on the old name)
- **Broken JS** → test fails (console error detected)
- **New page added** → ignored until explicitly declared in the list

> All page lists are **fixed and explicit**. Adding a new HTML file to the repo does not automatically include it in the test scope — it must be declared manually. This is intentional: it guarantees that only known, reviewed pages are part of the non-regression contract.

---

## Deployment

GitHub Pages is currently deployed via **Deploy from a branch** (configured in Settings → Pages → Build and deployment → Sources).

The workflow `.github/workflows/deploy-pages.yml` is **disabled** for now (`if: false` on both jobs). When ready, an admin can switch the source in Settings from "Deploy from a branch" to "GitHub Actions" — this workflow will then take over and produce a clean deployment by explicitly excluding:

- `tests/` — Playwright and Vitest specs
- `node_modules/` — npm dependencies
- `package.json` and `package-lock.json`
- `playwright.config.js` and `vitest.config.js`
- `README.md` and `api-design.md`
- `.gitignore`

---

## Continuous Integration

Non-regression tests run **automatically on every pull request** to the `main` branch via GitHub Actions (`.github/workflows/regression-tests.yml`).

If any test fails, the CI job fails and the deployment is blocked until the issue is resolved.

In case of failure, a full Playwright report is uploaded as a GitHub Actions artifact and kept for 7 days, allowing you to inspect screenshots and diffs directly from the Actions tab.

---

## Project Structure

```
.
├── tests/
│   ├── unit.spec.js          # Unit tests (HTML structure, title exact match for all pages, h1 presence)
│   ├── functional.spec.js    # Functional tests (HTTP 200 and no JS errors for all known pages)
│   ├── visual.spec.js        # Visual regression tests (screenshot diff)
│   └── snapshots/            # Reference screenshots (committed to the repo)
├── .github/
│   └── workflows/
│       └── regression-tests.yml
├── vitest.config.js
└── package.json
```

---

## What Each Test Layer Checks

### Unit tests (`unit.spec.js`)
For every known HTML page:
- Exactly one `<h1>` per page
- A non-empty `<title>` tag (with exact content check for all known pages)

### Functional tests (`functional.spec.js`)
For every known HTML page:
- Page responds with HTTP 200
- No JavaScript errors in the browser console

### Visual regression tests (`visual.spec.js`)
For every known HTML page:
- Full-page screenshot is compared against the reference baseline
- A diff above 2% pixel ratio causes the test to fail

---

## Setup

```bash
# Install dependencies
npm install

# Install Playwright browser
npx playwright install chromium

# Generate visual reference screenshots (run once, then commit)
npm run test:visual:update
git add tests/snapshots/
git commit -m "chore: add visual regression baselines"
```

---

## Running the Tests

```bash
# Run all tests
npm test

# Run unit tests only
npm run test:unit

# Run functional tests only
npm run test:functional

# Run visual regression tests only
npm run test:visual

# Update visual snapshots after an intentional UI change
npm run test:visual:update
```

---

## Adding a New Page

When a new HTML page is added to the site, update the page list in **all three spec files**:

1. `tests/unit.spec.js` — add an entry to the `pages` array
2. `tests/functional.spec.js` — add an entry to the `knownPages` array
3. `tests/visual.spec.js` — add an entry to the `criticalPages` array

Then regenerate the visual baseline for the new page:

```bash
npm run test:visual:update
git add tests/snapshots/
git commit -m "chore: add snapshot for <page-name>"
```

Then regenerate the Linux baselines for CI by triggering the **Update Visual Snapshots** workflow:

1. Go to **Actions** → **Update Visual Snapshots** on GitHub
2. Click **Run workflow** and select your branch
3. The workflow will generate the Linux snapshots and commit them to your branch
