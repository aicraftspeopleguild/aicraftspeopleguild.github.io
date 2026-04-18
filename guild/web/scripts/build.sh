#!/usr/bin/env bash
# ACG site build pipeline
# Orchestrates all content pipelines; produces guild/web/dist/
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
cd "$REPO"

echo "[build] 1/9 Extract components from engineering docs"
python guild/web/scripts/components/extract.py

echo ""
echo "[build] 2/9 Build component UDT/tag catalog"
python guild/web/scripts/components/build-catalog.py

echo ""
echo "[build] 3/9 Rebuild white paper UDT instances"
cd guild/web/white-papers && python ingest.py && cd "$REPO"

echo ""
echo "[build] 4/9 Generate white paper apps (one App per paper)"
python guild/web/scripts/apps/build-whitepaper-apps.py

echo ""
echo "[build] 5/9 Render view trees to dist/"
node guild/web/scripts/build.js

echo ""
echo "[build] 6/9 Overlay white-papers + members index from UDT instances"
python guild/web/scripts/white-papers/regen-index.py
python guild/web/scripts/members/regen-index.py

echo ""
echo "[build] 7/9 Rebuild Program UDT + tag catalog (from PackML state logs)"
python guild/web/scripts/build-programs.py

echo ""
echo "[build] 8/9 Render Perspective-schema views (acg.* components)"
node guild/web/scripts/perspective-build.js

echo ""
echo "[build] 9/9 Done. dist/ contains $(ls guild/web/dist/*.html 2>/dev/null | wc -l) pages."
