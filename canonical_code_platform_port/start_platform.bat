@echo off
setlocal

rem ========================================
rem Canonical Code Platform - Consolidated Launcher
rem ========================================

set "WORKDIR=%~dp0"
cd /d "%WORKDIR%"

rem Prefer project venv python if present
set "PY_EXE=python"
if exist ".venv\Scripts\python.exe" set "PY_EXE=.venv\Scripts\python.exe"

rem Ensure base folders exist
for %%D in ("staging" "staging\incoming" "staging\processed" "staging\failed" "bus" "logs") do (
    if not exist "%%~D" mkdir "%%~D"
)

rem Initialize orchestrator config if missing
if not exist "orchestrator_config.json" (
    echo Generating default orchestrator_config.json...
    "%PY_EXE%" orchestrator.py --init
    echo.
)

echo Starting orchestrator service...
start "Orchestrator" "%PY_EXE%" orchestrator.py

rem Give orchestrator a moment to start
if exist "%SystemRoot%\System32\timeout.exe" timeout /t 2 /nobreak >nul

echo Starting UI dashboard (http://localhost:8501)...
if exist "ui_app.py" (
    start "UI Dashboard" "%PY_EXE%" -m streamlit run ui_app.py
) else (
    echo ui_app.py not found; skipping UI startup.
)

echo.
echo Services launched. Press Ctrl+C in their windows to stop.

goto :eof

endlocal
