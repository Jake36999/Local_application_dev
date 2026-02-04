@echo off
REM =========================================
REM Directory Bundler v4.5 - Quick Launch
REM =========================================
REM This batch file provides one-click execution of the Directory Bundler

TITLE Directory Bundler v4.5 - Enhanced Code Analysis Tool

REM Change to the script directory
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/
    echo.
    pause
    exit /b 1
)

REM Display startup message
echo.
echo ========================================
echo  Directory Bundler v4.5
echo  Enhanced Code Analysis Tool
echo ========================================
echo.
echo Starting bundler...
echo.

REM Run the Python script
python Directory_bundler_v4.5.py

REM Check if script executed successfully
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Bundler encountered an error (Exit Code: %errorlevel%)
    echo.
    echo Common issues:
    echo  - Missing dependencies: Run 'pip install -r requirements.txt'
    echo  - Invalid directory path
    echo  - Permission issues
    echo.
)

REM Pause to keep window open
echo.
echo ========================================
pause
