@echo off
title ACP V1 Bootloader Service
color 0B

echo ===================================================
echo        ACP V1 BOOTLOADER & CONTROL PLANE
echo ===================================================
echo.

:: Set PYTHONPATH to current directory so imports work
set PYTHONPATH=%CD%

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    pause
    exit /b
)

echo [INFO] Root Directory: %CD%
echo [INFO] Starting FastAPI Uvicorn Server on Port 8000...
echo.

:: Launch the Module
python ops/bootloader/boot_api.py

pause
