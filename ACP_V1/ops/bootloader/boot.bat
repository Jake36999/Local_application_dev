@echo off
SETLOCAL
SET PYTHONPATH=%~dp0..\..\..
uvicorn ops.bootloader.boot_main:app --reload --port 8000
ENDLOCAL
