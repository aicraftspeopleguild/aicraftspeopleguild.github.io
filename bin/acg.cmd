@echo off
REM Windows dispatcher for `acg` — forwards to the Python script.
python "%~dp0acg" %*
