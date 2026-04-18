#!/usr/bin/env bash
# ACG site build pipeline
# Orchestrates all content pipelines; produces guild/web/dist/
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
cd "$REPO"

echo "[build] 1/12 Extract components from engineering docs"
python guild/web/scripts/components/extract.py

echo ""
echo "[build] 2/12 Build component UDT/tag catalog"
python guild/web/scripts/components/build-catalog.py

echo ""
echo "[build] 3/12 Rebuild white paper UDT instances"
cd guild/Enterprise/L4/api/white-papers && python ingest.py && cd "$REPO"

echo ""
echo "[build] 4/12 Generate white paper apps (one App per paper)"
python guild/web/scripts/apps/build-whitepaper-apps.py

echo ""
echo "[build] 5/12 Render view trees to dist/"
node guild/web/scripts/build.js

echo ""
echo "[build] 6/12 Overlay white-papers + members index from UDT instances"
python guild/web/scripts/white-papers/regen-index.py
python guild/web/scripts/members/regen-index.py

echo ""
echo "[build] 7/12 Rebuild Program UDT + tag catalog (from PackML state logs)"
python guild/web/scripts/build-programs.py
python guild/web/scripts/pages/build-path-graph.py

echo ""
echo "[build] 8/12 Render Perspective-schema views (acg.* components)"
node guild/web/scripts/perspective-build.js

echo ""
echo "[build] 9/12 Initialize SQLite databases (aggregate + per-directory tag.db)"
python guild/Enterprise/L4/database/init-db.py
python guild/web/scripts/db/build-local-tagdbs.py

echo ""
echo "[build] 10/12 Build static JSON API (/api/*.json)"
python guild/web/scripts/api/build-api.py

echo ""
echo "[build] 11/12 Build runtime tags + CSV catalogs + sitemap.xml"
python guild/web/scripts/api/build-runtime-tags.py
python guild/web/scripts/api/build-csv-catalog.py
python guild/web/scripts/api/build-sitemap.py

echo ""
echo "[build] 12/12 Done. dist/ contains $(ls guild/web/dist/*.html 2>/dev/null | wc -l) pages."
