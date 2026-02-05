@echo off
REM =========================================
REM Directory Bundler v4.5 - Test Suite Runner
REM =========================================
REM Run all tests with one click

TITLE Directory Bundler v4.5 - Test Suite

REM Change to the script directory
cd /d "%~dp0"

REM Check if pytest is installed
python -m pytest --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] pytest is not installed
    echo Installing pytest...
    pip install pytest pytest-cov
    echo.
)

REM Display startup message
echo.
echo ========================================
echo  Directory Bundler v4.5 - Test Suite
echo ========================================
echo.

REM Run tests with verbose output
python -m pytest test_bundler.py -v --tb=short

REM Display results
echo.
if %errorlevel% equ 0 (
    echo [SUCCESS] All tests passed!
) else (
    echo [FAILED] Some tests failed. Review output above.
)

echo.
echo ========================================
pause
