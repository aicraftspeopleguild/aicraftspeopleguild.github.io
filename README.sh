#!/usr/bin/env bash
# ACG · aicraftspeopleguild.github.io · root executable README
# Thin dispatcher that forwards to guild/web/scripts/README.sh.
# Run without args for help; pass a subcommand to execute.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
exec bash "$HERE/guild/web/scripts/README.sh" "$@"
