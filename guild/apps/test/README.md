# ACG-TEST

Konomi Standard · UDT-nested architecture for GitHub Actions testing.
AI Craftspeople Guild · v1.0 · April 2026.

This repo is both the reference documentation for the standard AND a
GitHub Pages site that applies the standard to itself — every page has a
`.test.yml` file, and the runner verifies each step of the build process.

## Layout

```
/
├── index.html                          entry point (GitHub Pages serves this)
├── pages/
│   ├── standard.html                   the full standard
│   ├── types.html                      per-UDT reference with live elements
│   ├── example.html                    article-notification rendered as UDTs
│   ├── runner.html                     in-browser test dashboard
│   └── terminal.html                   browser-side terminal
├── assets/
│   ├── style.css                       shared styles
│   ├── udt-elements.js                 custom elements: <udt-expectation> etc.
│   ├── runner-core.js                  pure parser + check functions
│   ├── test-runner.js                  page bootstrap that mounts results
│   └── terminal.js                     terminal command engine
├── tests/
│   ├── manifest.json                   list of test files
│   ├── index.test.yml                  one test per page
│   ├── standard.test.yml
│   ├── types.test.yml
│   ├── example.test.yml
│   ├── runner.test.yml
│   ├── terminal.test.yml
│   ├── deploy-pages.test.yml           canonical workflow test
│   └── process.test.yml                meta: every step has a verdict
├── paper-auto-index-standard.html      Guild paper (has acg-paper frontmatter)
├── papers.json                         machine-readable paper index (generated)
├── white-papers.html                   human-readable paper index (generated)
├── .github/
│   ├── workflows/
│   │   ├── deploy-pages.yml            publishes the site
│   │   └── paper-index.yml             auto-indexes papers on PR
│   └── scripts/
│       └── parse-papers.js             scan + fill + generate paper index
├── acg-test.config.yml                 runner config + extension notes
└── README.md
```

## UDT custom elements

Each type in the standard has a matching custom element, usable in any HTML:

```html
<udt-expectation expect="present" reason="..."></udt-expectation>
<udt-eventtrigger event="pull_request" types="opened" expect="triggered" reason="..."></udt-eventtrigger>
<udt-pathwatch path="articles/**" expect="triggered" reason="..."></udt-pathwatch>
<udt-guardrail condition="PR is a draft" reason="..."></udt-guardrail>
<udt-secret name="EMAIL_USERNAME" reason="..."></udt-secret>
<udt-notification type="email">
  <udt-field name="recipient" address="..." expect="present" reason="..."></udt-field>
</udt-notification>
<udt-workflowtest test="..." workflow="...">
  ...
</udt-workflowtest>
```

Every expectation-bearing element requires a `reason` attribute. The reason
IS the documentation — if a human can't read it and understand why the check
matters, the test is wrong.

## Running tests in the browser

Open the site via GitHub Pages (or any static server) and visit
`pages/runner.html`. The runner:

1. loads `tests/manifest.json`
2. fetches each `.test.yml`, parses it
3. fetches the target page / file
4. evaluates every expectation (watches, secrets, guardrails)
5. renders pass / fail / skip per the standard's three-result vocabulary

Results flow into `#site-summary` on every page and `#test-list` on the
runner page. The process-steps panel on the runner page shows the TDD phases
(scaffold → fail → write → pass → commit) and their live verdicts.

## Paper auto-index

The repo implements the
[Paper Auto-Index Standard](paper-auto-index-standard.html) (ACG-STD-AUTOPARSE-2026).
Every paper at the repo root carries an `acg-paper:` frontmatter block;
`.github/scripts/parse-papers.js` scans them, fills missing fields, and
regenerates `papers.json` and `white-papers.html`. The PR workflow
`.github/workflows/paper-index.yml` runs the parser on every paper change
and posts a summary comment. The standard indexes itself — the page that
defines the format is the first entry in the index.

Run the parser locally:

```
node .github/scripts/parse-papers.js
```

## Browser terminal

Open `pages/terminal.html`. Commands:

```
help                                show all commands
ls                                  list local tests in tests/manifest.json
cat <path>                          show a file from this site
run                                 run every local test
run <url-or-path>                   run a single .test.yml from anywhere
fetch <owner/repo[@ref]> <path>     run a .test.yml from a public GitHub repo
                                    e.g. fetch teslasolar/acg-test tests/index.test.yml
target <url>                        fetch any HTML and report basic UDT counts
paste                               open a textarea, paste YAML, run it
validate <url-or-path>              parse a test file and report shape only
init <name>                         print a blank .test.yml scaffold
report                              re-render the last summary
papers                              list papers.json
papers scan <url>                   scan any HTML URL for acg-paper frontmatter
clear, history, echo
```

Cross-origin targets are subject to CORS. `raw.githubusercontent.com` is
permissive for public repos, so `fetch <owner>/<repo> <path>` works for
anything you can read on GitHub.

## Running tests from the CLI

The standard defines the following commands (section 10 of the spec):

```
acg-test run <file>              run one test file
acg-test run tests/              run all tests in folder
acg-test init <workflow-name>    scaffold a blank test file
acg-test validate <file>         check test YAML structure only
acg-test report                  summary of all tests across repo
```

The in-browser runner in this repo is the reference implementation of the
test-evaluation semantics. A CLI implementation can be produced from the
same YAML files without modification.

## Local preview

```
python3 -m http.server 8080
```

then open <http://localhost:8080/>.

## Design rules

1. Every expectation has a reason.
2. Four words only: `present`, `triggered`, `not triggered`, `configured`.
3. Three results only: `pass`, `fail`, `skip`.
4. Tests before code.
5. UDT inheritance — every type traces back to `UDT:Expectation`.
6. One test file, one workflow. One test file, one page.

> if you can read English, you can read the test
