@echo off
title ACP V2 Interface
color 0E

echo ===================================================
echo           STARTING ACP REACT INTERFACE
echo ===================================================
echo.

echo [INFO] Injected Frontend Components and Services:
echo   [SERVICE]  ui/frontend/services/FrontendGeminiService.ts
echo   [HOOK]     ui/frontend/hooks/useOptimizedQuery.ts
echo   [COMP]     ui/frontend/components/SmartCodeRunner.tsx
echo   [COMP]     ui/frontend/components/P5StackVisualizer.tsx
echo   [COMP]     ui/frontend/components/LiveGraph.tsx
echo   ---
echo   [INFO] Components are now available in the React UI.
echo.

cd ui/frontend
call npm run dev
