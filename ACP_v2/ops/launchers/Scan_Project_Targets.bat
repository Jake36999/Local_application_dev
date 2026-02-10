@echo off
TITLE Aletheia Ingestion - Target Scan
CLS

REM Add the platform code to PYTHONPATH so Python can find the modules
set PYTHONPATH=%PYTHONPATH%;%CD%\canonical_code_platform_port

echo ========================================================
echo      ALETHEIA TARGET INGESTION (Skipping Platform)
echo ========================================================
echo.

REM 1. ACP_V1
echo [Target 1/5] Ingesting ACP_V1...
python canonical_code_platform_port\workflows\workflow_ingest.py ACP_V1
if %errorlevel% neq 0 echo [WARN] Failed to scan ACP_V1

REM 2. Ingest_pipeline_V4r
echo.
echo [Target 2/5] Ingesting Ingest_pipeline_V4r...
python canonical_code_platform_port\workflows\workflow_ingest.py Ingest_pipeline_V4r
if %errorlevel% neq 0 echo [WARN] Failed to scan Ingest_pipeline_V4r

REM 3. directory_bundler_port
echo.
echo [Target 3/5] Ingesting directory_bundler_port...
python canonical_code_platform_port\workflows\workflow_ingest.py directory_bundler_port
if %errorlevel% neq 0 echo [WARN] Failed to scan directory_bundler_port

REM 4. control_hub_port
echo.
echo [Target 4/5] Ingesting control_hub_port...
python canonical_code_platform_port\workflows\workflow_ingest.py control_hub_port
if %errorlevel% neq 0 echo [WARN] Failed to scan control_hub_port

REM 5. IRER_Validation_suite_run_ID-9
echo.
echo [Target 5/5] Ingesting IRER_Validation_suite_run_ID-9...
if exist "IRER_Validation_suite_run_ID-9" (
    python canonical_code_platform_port\workflows\workflow_ingest.py IRER_Validation_suite_run_ID-9
) else (
    echo [SKIP] Folder IRER_Validation_suite_run_ID-9 not found.
)

echo.
echo ========================================================
echo               ALL TARGETS PROCESSED
echo ========================================================
echo.
pause
