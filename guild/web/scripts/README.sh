#!/usr/bin/env bash
# ACG site build scripts — executable README + dispatcher.
#
# Run without arguments to print this help. Run with a subcommand to execute
# the matching script. All paths are resolved relative to the repo root.
#
# Usage: guild/web/scripts/README.sh [<command>]
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"

usage() {
  cat <<EOF

ACG Build Scripts
=================

Orchestrators (at scripts/ root)
--------------------------------
  build            Run the full site build pipeline (6 steps)
                   → bash $HERE/build.sh
  render           Render view trees to guild/web/dist/ only
                   → node $HERE/build.js

White paper pipeline (scripts/white-papers/)
--------------------------------------------
  papers:extract   Parse rendered HTML papers into originals/*.md
                   → python $HERE/white-papers/extract.py
  papers:regen     Regenerate white-papers.html from UDT instances
                   → python $HERE/white-papers/regen-index.py

Member pipeline (scripts/members/)
----------------------------------
  members:extract  Parse member HTML pages into originals/*.md + UDT instances
                   → python $HERE/members/extract.py
  members:regen    Regenerate members.html from Member UDT instances
                   → python $HERE/members/regen-index.py

Component pipeline (scripts/components/)
----------------------------------------
  components:extract   Extract Component UDTs from docs/engineering/ code blocks
                       → python $HERE/components/extract.py
  components:catalog   Build tag catalog (category → component IDs inverted index)
                       → python $HERE/components/build-catalog.py

Page decomposition (scripts/pages/)
-----------------------------------
  pages:decompose  Parse static HTML pages into view.json + data.json trees
                   → python $HERE/pages/decompose.py

Apps pipeline (scripts/apps/)
-----------------------------
  apps:papers      Generate one App per white paper UDT instance
                   (App + view binding + data.json with markdown→HTML)
                   → python $HERE/apps/build-whitepaper-apps.py

Docs split utilities (scripts/docs/)
------------------------------------
  docs:split-catalog  Split component-catalog/index.md into per-component files
                      → python $HERE/docs/split-catalog.py
  docs:split-udt      Split tech-spec/udt-system.md into per-type files
                      → python $HERE/docs/split-udt-spec.py

Data flow
---------
  originals/*.md  →  ingest.py  →  udts/instances/*.json
  udts/instances  →  regen-index →  dist/<index>.html
  view.json + data.json + components/udts/ → build.js → dist/<slug>.html

Paper Auto-Index Standard (.github/)
------------------------------------
  .github/scripts/parse-papers.js      Scan for acg-paper frontmatter
  .github/scripts/validate-index.js    Validate papers.json
  .github/scripts/generate-html.js     Generate white-papers.html from papers.json
  .github/workflows/paper-index.yml    PR-triggered auto-index workflow

EOF
}

case "${1:-help}" in
  help|--help|-h|"")       usage ;;
  build)                   bash "$HERE/build.sh" ;;
  render)                  node "$HERE/build.js" ;;
  papers:extract)          python "$HERE/white-papers/extract.py" ;;
  papers:regen)            python "$HERE/white-papers/regen-index.py" ;;
  members:extract)         python "$HERE/members/extract.py" ;;
  members:regen)           python "$HERE/members/regen-index.py" ;;
  components:extract)      python "$HERE/components/extract.py" ;;
  components:catalog)      python "$HERE/components/build-catalog.py" ;;
  pages:decompose)         python "$HERE/pages/decompose.py" ;;
  apps:papers)             python "$HERE/apps/build-whitepaper-apps.py" ;;
  test:links)              python "$HERE/test-links.py" ;;
  fix:links)               python "$HERE/fix-data-links.py" ;;
  docs:split-catalog)      python "$HERE/docs/split-catalog.py" ;;
  docs:split-udt)          python "$HERE/docs/split-udt-spec.py" ;;
  *)
    echo "Unknown command: $1" >&2
    echo "Run '$0 help' for usage." >&2
    exit 1
    ;;
esac
