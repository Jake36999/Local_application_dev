@echo off
title ACP Frontend Setup
color 0B

echo ===================================================
echo        INSTALLING FRONTEND DEPENDENCIES
echo ===================================================
echo.

node -v >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is NOT installed.
    echo Please download and install Node.js LTS from: https://nodejs.org/
    pause
    exit /b
)

echo [INFO] Installing packages (this may take a minute)...
call npm install

if %errorlevel% neq 0 (
    echo [ERROR] npm install failed.
    pause
    exit /b
)

echo.
echo [SUCCESS] Dependencies installed! You can now run the UI.
pause
