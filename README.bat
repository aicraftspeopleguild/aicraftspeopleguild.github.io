@echo off
REM ACG · aicraftspeopleguild.github.io · root executable README (Windows)
REM Thin dispatcher that forwards to guild/web/scripts/README.sh via bash.
REM Requires Git Bash or WSL on PATH.
bash "%~dp0guild\web\scripts\README.sh" %*
