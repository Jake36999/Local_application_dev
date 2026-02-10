@echo off
REM Launches ACP_V1 Bootloader FastAPI server via Uvicorn
SETLOCAL
SET PYTHONPATH=%~dp0..\..\..
uvicorn ops.bootloader.boot_api:app --host 0.0.0.0 --port 8090 --reload
ENDLOCAL