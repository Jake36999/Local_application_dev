import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Optional, Any, Type, Dict
from fastapi import FastAPI, Header, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- 1. Path Setup (Must be first) ---
file_path = Path(__file__).resolve()
PROJECT_ROOT = file_path.parents[2]  # ACP_v2 root
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# --- 2. Dynamic Imports ---
AgentFactory_imported = False
try:
    from core.identities.agent_factory import AgentFactory
    AgentFactory_imported = True
except ImportError:
    print("[WARN] AgentFactory not found in core/identities/agent_factory.py")

ScannerClass: Any = None
try:
    from tools.analysis.codebase_scanner import CodebaseScanner
    ScannerClass = CodebaseScanner
except ImportError:
    pass

# DB Logic
try:
    from tools.core.canon_db import init_db
except ImportError:
    def init_db(db_path: Any = ...) -> Any:
        pass

# --- 3. App Initialization ---
CANON_DB_PATH = PROJECT_ROOT / "memory/sql/project_meta.db"
if not CANON_DB_PATH.parent.exists():
    CANON_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

try: 
    init_db(str(CANON_DB_PATH))
except: 
    pass

app = FastAPI(title="Aletheia IDE", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 4. Models ---
class FileReadRequest(BaseModel):
    path: str

class FileWriteRequest(BaseModel):
    path: str
    content: str

class WorkflowRequest(BaseModel):
    name: str
    args: Optional[Dict[str, Any]] = {}

# --- 5. Helper Functions ---
async def verify_admin(x_api_key: Optional[str] = Header(None)):
    allowed_keys = ["dev_key", "your-admin-api-key"]
    if not x_api_key or x_api_key not in allowed_keys:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")

# --- 6. Endpoints ---

@app.get("/health")
def health():
    return {"status": "ok", "system": "ACP_v2"}


# --- Identity Endpoint (Dynamic System Prompts) ---
@app.get("/dev/identities")
async def list_identities(x_api_key: str = Header(...)):
    """
    Returns a list of available agent identities from core/identities.
    """
    await verify_admin(x_api_key)
    
    identities_dir = PROJECT_ROOT / "core" / "identities"
    if not identities_dir.exists():
        return {"status": "error", "identities": []}

    identities = []
    for item in identities_dir.iterdir():
        manifest_path = item / "10_manifest.json"
        if item.is_dir() and manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                identities.append({
                    "id": item.name,
                    "name": manifest.get("agent_name", item.name),
                    "role": manifest.get("role", "Assistant"),
                    "description": manifest.get("system_prompt", "")[:100] + "..."
                })
            except Exception as e:
                print(f"[WARN] Failed to load identity {item.name}: {e}")

    return {"status": "success", "identities": identities}

# --- Context Tools ---
@app.post("/dev/initialize-context")
async def initialize_dev_context(x_api_key: str = Header(...)):
    await verify_admin(x_api_key)
    if ScannerClass is None:
        return {"status": "error", "detail": "CodebaseScanner module not found."}

    scanner = ScannerClass(str(PROJECT_ROOT))
    snapshot = scanner.generate_system_snapshot()
    system_prompt = f"System Context:\n{snapshot}"
    
    return {
        "status": "initialized",
        "system_context": system_prompt,
        "token_estimate": len(system_prompt) / 4
    }

# --- Agentic Tools ---
@app.post("/dev/list-directory")
async def list_directory_endpoint(request: FileReadRequest, x_api_key: str = Header(...)):
    await verify_admin(x_api_key)
    try:
        target_path = (PROJECT_ROOT / request.path).resolve()
        if not str(target_path).startswith(str(PROJECT_ROOT)):
            raise HTTPException(status_code=403, detail="Access denied.")
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="Directory not found.")
            
        items = []
        for item in target_path.iterdir():
            if item.name.startswith(('.', '__')): continue
            kind = "DIR" if item.is_dir() else "FILE"
            items.append(f"[{kind}] {item.name}")
        return {"status": "success", "items": sorted(items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/dev/read-file")
async def read_file_content(request: FileReadRequest, x_api_key: str = Header(...)):
    await verify_admin(x_api_key)
    try:
        target_path = (PROJECT_ROOT / request.path).resolve()
        if not str(target_path).startswith(str(PROJECT_ROOT)):
            raise HTTPException(status_code=403, detail="Access denied.")
        if not target_path.exists() or not target_path.is_file():
            raise HTTPException(status_code=404, detail="File not found.")
        content = target_path.read_text(encoding="utf-8", errors="replace")
        return {"status": "success", "path": request.path, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/dev/write-file")
async def write_file_content(request: FileWriteRequest, x_api_key: str = Header(...)):
    await verify_admin(x_api_key)
    try:
        target_path = (PROJECT_ROOT / request.path).resolve()
        if not str(target_path).startswith(str(PROJECT_ROOT)):
            raise HTTPException(status_code=403, detail="Access denied.")
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(request.content, encoding="utf-8")
        return {"status": "success", "path": request.path, "bytes_written": len(request.content)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/dev/activate-workflow")
async def activate_workflow_endpoint(request: WorkflowRequest, x_api_key: str = Header(...)):
    await verify_admin(x_api_key)
    # Basic validation mapping
    workflow_map = {
        "workflow_ingest": "workflows/workflow_ingest.py",
        "workflow_analyze": "workflows/workflow_analyze.py",
        "workflow_verify": "workflows/workflow_verify.py",
        "workflow_build_stack": "workflows/workflow_build_stack.py",
        "workflow_extract": "workflows/workflow_extract.py",
        "workflow_validate_schema": "workflows/workflow_validate_schema.py"
    }
    
    if request.name not in workflow_map:
        raise HTTPException(status_code=400, detail=f"Unknown workflow: {request.name}")
        
    script_path = PROJECT_ROOT / workflow_map[request.name]
    if not script_path.exists():
        raise HTTPException(status_code=404, detail="Script not found.")

    try:
        print(f"[WORKFLOW] Triggering {request.name}...")
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT)
        )
        return {
            "status": "success" if result.returncode == 0 else "error",
            "workflow": request.name,
            "output": result.stdout + "\n" + result.stderr
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8090))
    print(f"Starting Backend on {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)