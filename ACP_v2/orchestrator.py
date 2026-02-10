from fastapi import APIRouter, Body, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import os
from pathlib import Path
from core.sentinel import SentinelGatekeeper
import logging
import subprocess
import sys
import time
import json

logger = logging.getLogger("orchestrator")

router = APIRouter()

# --- Authorization Dependency ---
async def verify_admin(x_api_key: str = Header(...)):
    if x_api_key != os.getenv("ADMIN_API_KEY", "dev_key"):
        raise HTTPException(status_code=403, detail="Invalid API Key")

# --- Session Manager Dependency ---
class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def get_session(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self._sessions:
            self._sessions[session_id] = {
                "active_lens": None,
                "dialectical_mode": False,
                "history": [],
                "metadata": {}
            }
        return self._sessions[session_id]

    def update_state(self, session_id: str, lens: str, dialectical: bool, metadata: Optional[Dict[str, Any]] = None):
        session = self.get_session(session_id)
        prev_state = {
            "lens": session.get("active_lens"),
            "dialectical": session.get("dialectical_mode"),
            "metadata": session.get("metadata", {})
        }
        session["active_lens"] = lens
        session["dialectical_mode"] = dialectical
        session["metadata"] = metadata or {}
        session["history"].append(prev_state)

    def batch_update(self, session_id: str, updates: list):
        session = self.get_session(session_id)
        for update in updates:
            self.update_state(
                session_id,
                update.get("lens", session["active_lens"]),
                update.get("dialectical", session["dialectical_mode"]),
                update.get("metadata", {})
            )

session_store = SessionManager()

async def get_current_session(x_session_id: str = Header(default="default_user")):
    return session_store.get_session(x_session_id)

# --- Pydantic Models ---
class CognitiveStateUpdate(BaseModel):
    lens: str = Field(..., description="Lens identifier")
    dialectical: bool = Field(..., description="Dialectical mode flag")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=lambda: {}, description="Optional metadata for state update")

class BatchStateUpdate(BaseModel):
    updates: list[CognitiveStateUpdate] = Field(..., description="List of state updates to apply in batch")

class CognitiveStateResponse(BaseModel):
    success: bool
    previous_lens: Optional[str]
    previous_dialectical: Optional[bool]
    current_lens: str
    current_dialectical: bool
    message: str
    metadata: Optional[Dict[str, Any]] = None

# --- Refactored Endpoints ---
@router.post(
    "/system/set-cognitive-state",
    response_model=CognitiveStateResponse,
    dependencies=[Depends(verify_admin)]
)
async def set_cognitive_state(
    update: CognitiveStateUpdate,
    x_session_id: str = Header(default="default_user"),
    session: Dict[str, Any] = Depends(get_current_session)
):
    prev_lens = str(session.get("active_lens") or "")
    prev_dialectical = bool(session.get("dialectical_mode"))
    try:
        session_store.update_state(x_session_id, update.lens, update.dialectical, update.metadata)
        return CognitiveStateResponse(
            success=True,
            previous_lens=prev_lens,
            previous_dialectical=prev_dialectical,
            current_lens=update.lens,
            current_dialectical=update.dialectical,
            message=f"State transitioned from lens={prev_lens}, dialectical={prev_dialectical} to lens={update.lens}, dialectical={update.dialectical}",
            metadata=update.metadata
        )
    except Exception as e:
        return CognitiveStateResponse(
            success=False,
            previous_lens=prev_lens,
            previous_dialectical=prev_dialectical,
            current_lens=prev_lens,
            current_dialectical=prev_dialectical,
            message=f"Error updating state: {e}",
            metadata=None
        )

@router.post(
    "/system/batch-cognitive-state",
    response_model=Dict[str, Any],
    dependencies=[Depends(verify_admin)]
)
async def batch_cognitive_state(
    batch: BatchStateUpdate,
    x_session_id: str = Header(default="default_user"),
    session: Dict[str, Any] = Depends(get_current_session)
):
    try:
        session_store.batch_update(x_session_id, [update.dict() for update in batch.updates])
        return {
            "success": True,
            "message": f"Batch update applied for {len(batch.updates)} states.",
            "history": session.get("history", [])
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error in batch update: {e}",
            "history": session.get("history", [])
        }

@router.get("/system/cognitive-state")
async def get_cognitive_state(
    session: Dict[str, Any] = Depends(get_current_session)
):
    return {
        "current_lens": session.get("active_lens"),
        "current_dialectical": session.get("dialectical_mode"),
        "metadata": session.get("metadata", {}),
        "history": session.get("history", [])
    }

class Orchestrator:
    def __init__(self, config_path: str = "config/orchestrator_config.json"):
        self.config_path = config_path
        self.config = self._load_config(config_path)
        # --- SENTINEL INITIALIZATION ---
        self.sentinel = SentinelGatekeeper(self.config)
        # -------------------------------
        # self.bus = MessageBus()  # MessageBus not available
        # ...existing code...

    def _load_config(self, config_path: str):
        # Placeholder: load config from file
        return {}

    def _handle_failed_file(self, file_path: Path):
        # Placeholder: handle failed file
        logging.warning(f"Failed file: {file_path}")

    def _move_to_queue_file(self, file_path: Path):
        # Placeholder: move file to queue
        logging.info(f"Moved {file_path} to queue.")
        return file_path

    def _process_staging_file(self, file_path: Path):
        """Process a file from staging folder."""
        logger.info(f"Processing {file_path.name}...")
        # --- WORKFLOW I: SENTINEL GATEKEEPER CHECK ---
        if not self.sentinel.audit_file(file_path):
            logger.error(f"Sentinel blocked {file_path.name} - moving to failed.")
            self._handle_failed_file(file_path)
            return
        # ---------------------------------------------
        try:
            staged_path = self._move_to_queue_file(file_path)
            pass
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")
            self._handle_failed_file(file_path)

def start_frontend():
    print("Starting frontend (npm run dev)...")
    subprocess.Popen(["npm", "run", "dev"], cwd="./ui")

def start_backend():
    print("Starting backend (main_platform.py)...")
    subprocess.Popen([sys.executable, "main_platform.py"])

def prompt_inflection():
    response = input("Ready for system inflection? (y/N): ")
    return response.lower() == "y"

def fetch_system_snapshot():
    import requests
    print("Fetching system snapshot from backend...")
    headers = {"x-api-key": "dev_key"}
    resp = requests.post("http://localhost:8090/dev/initialize-context", headers=headers)
    if resp.status_code == 200:
        with open("system_context.json", "w", encoding="utf-8") as f:
            json.dump(resp.json(), f, indent=2)
        print(f"Snapshot saved to system_context.json")
    else:
        print(f"Error: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    start_frontend()
    time.sleep(2)  # Wait for frontend to start
    start_backend()
    time.sleep(2)  # Wait for backend to start
    if prompt_inflection():
        fetch_system_snapshot()
        print("Send system_context.json to LM Studio Assistant for review.")
    else:
        print("Inflection skipped.")