@echo off
title Aletheia Backend Initializer
echo ===========================================
echo      ALETHEIA AUTO-PROVISIONING
echo ===========================================

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    pause
    exit
)

:: 2. Run Orchestrator
echo [1/4] Starting Orchestration Sequence...
python backend_startup.py

if %errorlevel% neq 0 (
    color 0C
    echo [FAILURE] Initialization failed. Check logs.
    pause
    exit
)

color 0A
echo.
echo [SUCCESS] Backend Initialized.
echo [INFO] Context State: ACTIVE
echo [INFO] Memory: HYDRATED
echo [INFO] Bus Signal: SENT
echo.
pause
