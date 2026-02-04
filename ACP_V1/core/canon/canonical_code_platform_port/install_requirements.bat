@echo off
setlocal

rem Install project requirements using the best available Python

set "WORKDIR=%~dp0"
cd /d "%WORKDIR%"

set "PY_EXE=python"
if exist ".venv\Scripts\python.exe" set "PY_EXE=.venv\Scripts\python.exe"

if not exist "requirements.txt" (
    echo requirements.txt not found in %WORKDIR%
    exit /b 1
)

echo Using Python: %PY_EXE%
"%PY_EXE%" -m pip install --upgrade pip
"%PY_EXE%" -m pip install -r requirements.txt

echo.
echo Requirements installation complete.

endlocal
