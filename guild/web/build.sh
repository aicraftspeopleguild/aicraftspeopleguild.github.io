#!/usr/bin/env bash
# ACG site build pipeline
# Runs all generators in the correct order, producing guild/web/dist/
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
cd "$REPO"

echo "[build] 1/5 Extract components from engineering docs"
python guild/web/extract-components.py

echo ""
echo "[build] 2/5 Rebuild white paper UDT instances"
cd guild/web/white-papers && python ingest.py && cd "$REPO"

echo ""
echo "[build] 3/5 Render view trees to dist/"
node guild/web/build.js

echo ""
echo "[build] 4/5 Overlay white-papers + members index from UDT instances"
python guild/web/white-papers/regen-index.py
python guild/web/members/regen-index.py

echo ""
echo "[build] 5/5 Done. dist/ contains $(ls guild/web/dist/*.html 2>/dev/null | wc -l) pages."
