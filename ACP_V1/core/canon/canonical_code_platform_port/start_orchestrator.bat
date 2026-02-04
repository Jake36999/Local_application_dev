@echo off
REM ========================================
REM Canonical Code Platform
REM Orchestrator Startup Script
REM ========================================

echo.
echo ========================================
echo  CANONICAL CODE PLATFORM
echo  ORCHESTRATOR & MESSAGE BUS
echo ========================================
echo.

REM Check if orchestrator_config.json exists
if not exist "orchestrator_config.json" (
    echo Generating default configuration...
    python orchestrator.py --init
    echo Configuration created: orchestrator_config.json
    echo.
)

REM Create required directories
if not exist "staging\incoming" mkdir staging\incoming
if not exist "staging\processed" mkdir staging\processed
if not exist "staging\failed" mkdir staging\failed
if not exist "bus" mkdir bus
if not exist "logs" mkdir logs

echo Starting orchestrator service...
echo Monitoring staging/incoming/ for files every 5 seconds...
echo Message bus listening on orchestrator_bus.db...
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

REM Start orchestrator in background
start "Orchestrator" python orchestrator.py

REM Give it time to start
timeout /t 2 /nobreak

REM Start UI in separate window (optional)
if exist "ui_app.py" (
    echo.
    echo Starting UI dashboard...
    echo Opening http://localhost:8501
    start "UI Dashboard" streamlit run ui_app.py
)

REM Keep this window open
pause
