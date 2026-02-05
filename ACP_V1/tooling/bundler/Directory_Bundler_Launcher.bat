@echo off
REM Unified launcher for Directory Bundler v4.5
setlocal enabledelayedexpansion

REM Change to script directory
cd /d "%~dp0"

REM Pre-flight: ensure Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH. Install Python 3.11+ and retry.
    pause
    exit /b 1
)

:menu
echo.
echo ========================================
echo Directory Bundler v4.5 - Launcher
echo ========================================
echo [1] Run Directory Bundler (CLI)
echo [2] Run Web Interface (port 8000)
echo [3] Run Tests (pytest)
echo [4] Install/Verify Dependencies
echo [5] Quit
echo.
choice /c 12345 /n /m "Select option (1-5): "
set "opt=%errorlevel%"
echo.
if "%opt%"=="5" goto :eof
if "%opt%"=="1" goto run_cli
if "%opt%"=="2" goto run_web
if "%opt%"=="3" goto run_tests
if "%opt%"=="4" goto run_install
goto menu

:run_cli
echo Starting Directory Bundler (CLI)...
python Directory_bundler_v4.5.py
if errorlevel 1 (
    echo.
    echo [ERROR] Bundler exited with code %errorlevel%.
    echo Common fixes: install deps (pip install -r requirements.txt), check paths/permissions.
)
pause
goto menu

:run_web
if "%WEB_PORT%"=="" set "WEB_PORT=8000"
echo Starting Directory Bundler Web Interface on http://localhost:%WEB_PORT%
if "%ENABLE_LMS_BOOTSTRAP%"=="1" (
    set "LMS_MODEL=%LM_BOOTSTRAP_MODEL%"
    if "%LMS_MODEL%"=="" set "LMS_MODEL=astral-4b-coder"
    where lms >nul 2>&1
    if %errorlevel%==0 (
        echo Bootstrapping LM Studio (server + load %LMS_MODEL%)...
        call lms server start --port 1234 --background
        call lms load --ttl 3600 --gpu max "%LMS_MODEL%"
    ) else (
        echo [WARN] ENABLE_LMS_BOOTSTRAP is set but 'lms' CLI not found in PATH.
    )
    echo.
)
goto check_port

:check_port
python -c "import socket, os, sys; port=int(os.environ.get('WEB_PORT','8000')); s=socket.socket();\
try: s.bind(('127.0.0.1', port)); s.close(); sys.exit(0)\
except OSError: sys.exit(1)" >nul 2>&1
if errorlevel 1 (
    echo [WARN] Port %WEB_PORT% is in use.
    set "FALLBACK_PORT=8010"
    choice /c RFCA /n /m "[R]etry, [F]orce-close on this port, [C]hange port, [A]bort: "
    set "sel=%errorlevel%"
    if "!sel!"=="1" (
        echo Close the process using port %WEB_PORT% then press any key to retry...
        pause >nul
        goto check_port
    )
    if "!sel!"=="2" (
        echo Attempting to terminate listeners on port %WEB_PORT%...
        for /f "tokens=5" %%p in ('netstat -aon ^| findstr ":%WEB_PORT% " ^| findstr LISTENING') do (
            taskkill /PID %%p /F >nul 2>&1
        )
        echo Re-checking port %WEB_PORT%...
        goto check_port
    )
    if "!sel!"=="3" (
        set /p WEB_PORT=Enter alternate port (default !FALLBACK_PORT!): 
        if "!WEB_PORT!"=="" set "WEB_PORT=!FALLBACK_PORT!"
        echo Trying port !WEB_PORT!...
        goto check_port
    )
    if "!sel!"=="4" goto menu
)

echo Starting API server in this window.
echo Press Ctrl+C to stop.
echo Opening browser to http://localhost:%WEB_PORT% ...
start "" "http://localhost:%WEB_PORT%"
python Directory_bundler_v4.5.py --web
set "srv_rc=%errorlevel%"
if not "!srv_rc!"=="0" (
    echo [ERROR] API server exited with code %srv_rc%.
    echo Check dependencies (pip install -r requirements.txt) and that no other service is occupying the port.
    pause
    goto menu
)
pause
goto menu

:run_tests
echo Checking pytest...
python -m pytest --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pytest not found; installing pytest and pytest-cov...
    pip install pytest pytest-cov
    echo.
)
echo Running tests...
python -m pytest test_bundler.py -v --tb=short
if %errorlevel% equ 0 (
    echo [SUCCESS] All tests passed!
) else (
    echo [FAILED] Some tests failed. Review output above.
)
pause
goto menu

:run_install
echo Installing dependencies from requirements.txt ...
pip install -r requirements.txt
if %errorlevel% equ 0 (
    if exist verify_setup.py (
        echo Running verify_setup.py ...
        python verify_setup.py
    )
    echo.
    echo [SUCCESS] Dependencies installed.
) else (
    echo.
    echo [ERROR] Dependency installation failed. Try upgrading pip and retry.
)
pause
goto menu
