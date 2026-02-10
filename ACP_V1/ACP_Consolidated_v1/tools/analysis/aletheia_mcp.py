
from mcp.server.fastmcp import FastMCP
import sqlite3
import sys
import os
import requests
import time
from pathlib import Path

# --- PATH SETUP ---
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

# --- IMPORTS ---
try:
    from tooling.common import security, profiler
    from core.canon import scanner as canon_scanner
except ImportError:
    class Mock:
        def __getattr__(self, name): return lambda *args, **kwargs: "Tool Unavailable"
    security = profiler = canon_scanner = Mock()

# Initialize
mcp = FastMCP("Aletheia Factory Manager")
BOOT_API = "http://localhost:8000"

def self_healing_tool(func):
    """Decorator: If tool fails, check system health and attempt repair."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as tool_error:
            try:
                # 1. Check Health
                health = requests.get(f"{BOOT_API}/system/health", timeout=1).json()
                # 2. Attempt Repair if Degraded
                if health.get("status") != "HEALTHY":
                    print(f"⚠️ System Degraded. Triggering Self-Repair...")
                    requests.post(f"{BOOT_API}/system/init")
                    time.sleep(2) # Wait for repair
                    return func(*args, **kwargs) # Retry
            except Exception as healing_error:
                return f"Tool Error: {tool_error}. (Self-Healing Failed: {healing_error})"
            return f"Tool Error: {tool_error}"
    return wrapper

def get_db():
    db_path = os.path.join(ROOT_DIR, "memory", "sql", "memory/sql/project_meta.db")
    return sqlite3.connect(db_path, check_same_thread=False)

@mcp.tool()
def read_system_state() -> str:
    """Reads the active context from safe_ops/context/active."""
    PERCEPTION_ROOT = Path(ROOT_DIR) / "safe_ops" / "context" / "active"
    if not PERCEPTION_ROOT.exists(): return "Error: Context not initialized."
    files = list(PERCEPTION_ROOT.glob("*"))
    return f"Active Context ({len(files)} files):\n" + "\n".join([f"- {f.name}" for f in files])

@mcp.tool()
@self_healing_tool
def profile_target(path: str) -> str:
    """Check file metadata/safety."""
    if not security.validate_path(path): return "Error: Security Violation"
    return str(profiler.profile_target(path))

@mcp.tool()
@self_healing_tool
def scan_code_structure(path: str) -> str:
    """Index code logic to DB (Deep AST Scan)."""
    if not security.validate_path(path): return "Error: Security Violation"
    conn = get_db()
    try:
        return str(canon_scanner.canon_scan(path, conn))
    finally:
        conn.close()

if __name__ == "__main__":
    mcp.run()