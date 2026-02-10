from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import logging
import sys
import os


# --- Path Setup ---
# Calculate Root: ACP_V1/ops/bootloader -> ../../ -> ACP_V1
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from ops.bootloader.initializer import SystemInitializer
from ops.bootloader.dep_manager import DependencyManager

# --- FIX 3: CORRECT IMPORT PATHS ---
# Was: from core.graph_transformer import ...
# Now: Point to tools.core and tools.api
from tools.core.graph_transformer import router as graph_router
from tools.core.lens_manager import router as lens_router
from tools.api.ws_runner import router as ws_runner_router

# --- Logging ---
log_path = ROOT_DIR / "logs/bootloader.log"
log_path.parent.mkdir(exist_ok=True)
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("acp.api")

# --- App Definition ---


app = FastAPI(title="ACP Bootloader", version="1.0")

# --- 🔓 CORS CONFIGURATION (The Bridge) ---
# --- CORS CONFIGURATION (The Bridge) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (Safe for local dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ------------------------------------------

initializer = SystemInitializer(ROOT_DIR)
dep_man = DependencyManager(ROOT_DIR)

# --- Models ---
class InitResponse(BaseModel):
    status: str
    directories_created: list
    db_status: str
    env_check: dict

class HealthResponse(BaseModel):
    status: str
    binaries: dict
    database: bool


# --- Register Routers ---
app.include_router(graph_router)
app.include_router(lens_router)
app.include_router(ws_runner_router)

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"status": "Aletheia API Online"}

@app.post("/system/init", response_model=InitResponse)
async def initialize_system():
    """Triggers the full initialization sequence."""
    try:
        logger.info("Initialization requested.")
        env = initializer.check_environment()
        dirs = initializer.scaffold_directories()
        db_msg = initializer.hydrate_databases()
        
        # Consolidate deps in background
        dep_man.consolidate_requirements()
        
        return {
            "status": "System Initialized",
            "directories_created": dirs,
            "db_status": db_msg,
            "env_check": env
        }
    except Exception as e:
        logger.error(f"Init failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/system/clean")
async def clean_system(confirm: bool = False):
    """Hard Reset: Moves active context to archive."""
    if not confirm:
        raise HTTPException(status_code=400, detail="Confirmation required (set confirm=True)")
    
    count = initializer.clean_context()
    return {"status": "Cleaned", "files_archived": count}

@app.get("/system/health", response_model=HealthResponse)
async def check_health():
    """Checks dependencies and DB connectivity."""
    bins = dep_man.check_system_binaries()
    db_ok = (ROOT_DIR / "memory/sql/project_meta.db").exists()
    
    status = "HEALTHY" if all(bins.values()) and db_ok else "DEGRADED"
    
    return {
        "status": status,
        "binaries": bins,
        "database": db_ok
    }

@app.get("/system/config")
async def get_config():
    """Reads the startup yaml (Read-Only)."""
    cfg_path = ROOT_DIR / "config/startup.yaml"
    if cfg_path.exists():
        return {"source": str(cfg_path), "content_preview": cfg_path.read_text()[:500]}
    return {"error": "Config missing"}

app.include_router(graph_router)
app.include_router(lens_router)
app.include_router(ws_runner_router)

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Bootloader starting for root: {ROOT_DIR}")
    uvicorn.run(app, host="127.0.0.1", port=8000)
