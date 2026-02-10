@echo off
REM ========================================
REM Canonical Code Platform - Quick Start
REM ========================================
REM
REM Double-click this file to launch the UI

echo.
echo ========================================
echo  Canonical Code Platform
echo  Starting UI...
echo ========================================
echo.

REM Check if canon.db exists
if not exist "canon.db" (
    echo WARNING: canon.db not found!
    echo.
    echo To get started:
    echo   1. Close this window when browser opens
    echo   2. Run: python workflows/workflow_ingest.py myfile.py
    echo   3. Re-run this start.bat file
    echo.
    echo Press any key to continue anyway...
    pause >nul
)

REM Launch Streamlit UI
echo Starting Streamlit UI...
echo Browser will open automatically at http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

streamlit run ui_app.py

REM If streamlit command fails
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Streamlit not found!
    echo ========================================
    echo.
    echo Install Streamlit:
    echo   pip install streamlit
    echo.
    echo Then run this file again.
    echo.
    pause
)
