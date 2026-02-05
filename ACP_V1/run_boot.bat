@echo off
title ACP V1 Bootloader Service
color 0B

echo ===================================================
echo        ACP V1 BOOTLOADER & CONTROL PLANE
echo ===================================================
echo.

echo [INFO] Injected Agentic Tools and Components:
echo   [OPS]  tools/ops/tool_forge_identity.py
echo   [OPS]  tools/ops/tool_equip_identity.py
echo   [OPS]  tools/ops/tool_forge_lens.py
echo   [OPS]  tools/ops/tool_create_spore.py
echo   [OPS]  tools/ops/tool_architect_agent.py
echo   [OPS]  tools/ops/tool_harvest_run_data.py
echo   [DEV]  tools/dev/tool_audit_physics.py
echo   [FRONTEND] ui/frontend/services/FrontendGeminiService.ts
echo   [FRONTEND] ui/frontend/hooks/useOptimizedQuery.ts
echo   [FRONTEND] ui/frontend/components/SmartCodeRunner.tsx
echo   [FRONTEND] ui/frontend/components/P5StackVisualizer.tsx
echo   [FRONTEND] ui/frontend/components/LiveGraph.tsx
echo   ---
echo   [INFO] Tools are now available for use in the ACP_V1 platform.
echo.

:: Set PYTHONPATH to current directory so imports work
set PYTHONPATH=%CD%

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    pause
    exit /b
)

echo [INFO] Root Directory: %CD%
echo [INFO] Starting FastAPI Uvicorn Server on Port 8000...
echo.

:: Launch the Module
python ops/bootloader/boot_api.py

pause
