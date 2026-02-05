import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import shutil
import os
import sqlite3
import subprocess
import requests

ACP_ROOT = Path(__file__).resolve().parents[2]
LOG_PATH = ACP_ROOT / "logs" / "bootloader.log"
logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("bootloader")

app = FastAPI(title="ACP_V1 Bootloader", version="1.0")

from typing import Optional

class HealthStatus(BaseModel):
    status: str
    model: Optional[str] = None

class InitResponse(BaseModel):
    directories: list
    db_exists: bool
    vector_writable: bool

class SanitizeResponse(BaseModel):
    moved_files: list

@app.post("/init", response_model=InitResponse)
async def init_system():
    created = []
    # Ensure required directories
    required_dirs = [
        ACP_ROOT / "memory" / "sql",
        ACP_ROOT / "memory" / "vector",
        ACP_ROOT / "logs",
    ]
    for d in required_dirs:
        if not d.exists():
            d.mkdir(parents=True, exist_ok=True)
            created.append(str(d.relative_to(ACP_ROOT)))
    # Ensure DB
    db_path = ACP_ROOT / "memory" / "sql" / "memory/sql/project_meta.db"
    db_exists = db_path.exists()
    if not db_exists:
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS meta (id INTEGER PRIMARY KEY, key TEXT, value TEXT);")
        conn.commit()
        conn.close()
    # Vector DB writable check
    vector_dir = ACP_ROOT / "memory" / "vector"
    test_file = vector_dir / "test_write.tmp"
    try:
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        vector_writable = True
    except Exception:
        vector_writable = False
    return InitResponse(
        directories=created,
        db_exists=db_path.exists(),
        vector_writable=vector_writable
    )

@app.get("/health", response_model=HealthStatus)
async def health_check():
    lm_url = os.environ.get("LM_STUDIO_URL", "http://localhost:1234")
    try:
        res = requests.get(f"{lm_url}/v1/models", timeout=2)
        if res.status_code == 200:
            data = res.json()
            model = data["data"][0]["id"] if "data" in data and data["data"] else "Unknown"
            return HealthStatus(status="ONLINE", model=model)
        else:
            return HealthStatus(status="OFFLINE")
    except Exception:
        return HealthStatus(status="OFFLINE")

@app.post("/sanitize", response_model=SanitizeResponse)
async def sanitize_context():
    active_dir = ACP_ROOT / "safe_ops" / "context" / "active"
    archive_dir = ACP_ROOT / "safe_ops" / "context" / "archive"
    moved = []
    if active_dir.exists():
        archive_dir.mkdir(parents=True, exist_ok=True)
        for f in active_dir.iterdir():
            if f.is_file():
                dest = archive_dir / f.name
                shutil.move(str(f), str(dest))
                moved.append(f.name)
    return SanitizeResponse(moved_files=moved)
