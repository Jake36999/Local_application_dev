@echo off
REM =========================================
REM Directory Bundler v4.5 - Dependency Installer
REM =========================================
REM Install all required Python packages

TITLE Directory Bundler v4.5 - Setup

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

echo.
echo ========================================
echo  Directory Bundler v4.5 - Setup
echo ========================================
echo.
echo This will install all required dependencies:
echo  - requests (HTTP library)
echo  - types-requests (Type stubs)
echo  - pytest (Testing framework)
echo  - pytest-cov (Coverage reports)
echo.
pause

echo.
echo Installing dependencies...
echo.

pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo [SUCCESS] All dependencies installed!
    echo ========================================
    echo.
    echo Verifying installation...
    python verify_setup.py
) else (
    echo.
    echo [ERROR] Installation failed
    echo Try running: pip install --upgrade pip
    echo Then run this script again
)

echo.
echo ========================================
pause
