# Level Map — Which Guild Asset Lives Where

Quick reference for mapping every concrete Guild artefact to its ISA-95 level.

| Asset                                       | Level | Kind             |
|---------------------------------------------|-------|------------------|
| A paper being drafted in an editor          | 0     | Physical work    |
| Mob programming session happening in a room | 0     | Physical work    |
| A ritual being practiced                    | 0     | Physical work    |
| `git commit` on a PR branch                 | 1     | Sensor           |
| `pull_request` webhook event                | 1     | Sensor           |
| Google Form submission                      | 1     | Sensor           |
| Submit form POST → hidden iframe            | 1     | Sensor           |
| PR status check update                      | 1     | Actuator         |
| Git commit from `guild-bot`                 | 1     | Actuator         |
| `.github/workflows/paper-index.yml`         | 1→2   | Event router     |
| PackML state machine (`lib/packml.py`)      | 2     | SCADA            |
| `guild/web/scripts/state/*.state.json`      | 2     | Run record       |
| `packml_runs` table                         | 2     | Run history      |
| Build pipeline `build.sh`                   | 3     | MES dispatcher   |
| `build-whitepaper-apps.py`                  | 3     | MES workflow step|
| `parse-papers.js`                           | 3     | MES parser       |
| `test-links.py` / `test-browser.js`         | 3     | MES QA           |
| `docs/engineering/`                         | 3     | MES document ctl |
| `docs/engineering/standards/*.md`           | 3     | Process contract |
| `guild/web/components/udts/*`               | 3     | Design artefact  |
| `guild/web/members/udts/instances/*.json`   | 4     | ERP master data  |
| `guild/web/white-papers/udts/instances/*`   | 4     | ERP master data  |
| `guild/Enterprise/L4/database/acg.db`                 | 4     | ERP data store   |
| `/api/papers.json`                          | 4     | ERP read API     |
| `/api/members.json`                         | 4     | ERP read API     |
| `/api/health.json`                          | 4     | ERP vitals       |
| Charter / Code of Conduct / Mission         | 4     | Governance       |
| Manifesto + signatories                     | 4     | Enterprise HR    |
| Tag catalog (`tags/index.json`)             | 4     | ERP taxonomy     |
| Path UDT instances                          | 4     | ERP routing      |

## Rule of thumb

- If humans write it → **L0**
- If a webhook fires on it → **L1**
- If a state machine supervises it → **L2**
- If a workflow schedules it → **L3**
- If you query it long after the fact → **L4**
