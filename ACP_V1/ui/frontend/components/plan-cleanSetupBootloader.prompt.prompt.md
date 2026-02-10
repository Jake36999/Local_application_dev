## Plan: Clean Setup & Bootloader Module for ACP_V1

Develop a modular FastAPI-based bootloader for ACP_V1, providing REST endpoints for initialization, cleaning, health checks, and configuration reporting. The solution will use dynamic path resolution, async endpoints, Pydantic models, and robust logging, with all logic and dependencies separated for maintainability.

### Steps
1. **Create Directory Structure**: Ensure `Local_application_dev/ACP_V1/ops/bootloader` exists.
2. **Implement `initializer.py`**:  
   - Create `SystemInitializer` class for environment validation, directory scaffolding, DB hydration, and vector DB checks.
3. **Implement `dep_manager.py`**:  
   - Add functions to consolidate requirements and check for system binaries (git, tesseract).
4. **Implement `boot_api.py`**:  
   - Build FastAPI app with async endpoints:  
     - `POST /system/init` (full setup)  
     - `POST /system/clean` (hard reset with confirmation)  
     - `GET /system/health` (subsystem status)  
     - `GET /system/config` (sanitized config)
   - Use Pydantic models for all request/response schemas.
   - Integrate logging and error handling (detailed stack traces in debug).
5. **Create `run_boot.bat`**:  
   - Batch script to launch the FastAPI server via Uvicorn with correct PYTHONPATH.

### Further Considerations
1. **Config Import**: Ensure all config loads from `ACP_V1/config/settings.py` (no local .env).
2. **Security**: Import and use `tooling.common.security` for path validation if available.
3. **Testing**: Consider endpoint and integration tests after initial deployment.

Let me know if you want to proceed with this plan or need adjustments before implementation.
