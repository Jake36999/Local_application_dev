@echo off
setlocal
title Aletheia Workspace Packager
cd /d "%~dp0"
set "PY=python"
where py >NUL 2>&1
if %ERRORLEVEL%==0 (
  set "PY=py -3"
)
echo =================================================
echo      ALETHEIA WORKSPACE PACKAGER
echo =================================================
echo [*] Target: Creating Versioned Bundle
echo.
if not exist "workspace_packager.py" (
    echo [ERROR] workspace_packager.py not found in root.
    pause
    exit /b 1
)
  REM --- FIX: Run the new root-level packager ---
  %PY% workspace_packager.py
if %ERRORLEVEL% NEQ 0 (
  echo.
  echo ❌ Packaging failed!
  pause
  exit /b 1
)
echo.
echo ✅ Workspace successfully packaged.
echo.
pause
