from mcp.server.fastmcp import FastMCP
import sqlite3
import sys
import os
from pathlib import Path
import glob

# Ensure we can import from 'core' if it exists in this directory
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "core"))

# Try importing tools. 
try:
    from tools import profiler, security, canon_scanner, pdf_scanner, test_runner
except ImportError:
    # Fallback/Placeholder if imports fail due to migration
    print("⚠️ Warning: Could not import 'tools'. Running in restricted mode.")
    class MockTool:
        def profile_target(self, p): return "Tool Missing"
        def canon_scan(self, p, c): return "Tool Missing"
        def run_tests(self, p): return {"passed": False, "full_log": "Tool Missing"}
    profiler = security = canon_scanner = pdf_scanner = test_runner = MockTool()
    security.validate_path = lambda p: True

# Initialize
mcp = FastMCP("Aletheia Factory Manager")

def get_db():
    db_path = Path("memory/sql/project_meta.db")
    if not db_path.parent.exists():
        os.makedirs(db_path.parent, exist_ok=True)
    return sqlite3.connect(str(db_path), check_same_thread=False)

@mcp.tool()
def read_system_state() -> str:
    """Restricted to the 'Active' context folder."""
    PERCEPTION_ROOT = Path(__file__).parent / "Context_State" / "Active"
    if not PERCEPTION_ROOT.exists():
        return "Error: System not initialized. Run start_backend.bat first."
    
    files = list(PERCEPTION_ROOT.glob("*"))
    summary = "Current Active Context:\n"
    content = ""
    
    for f in files:
        summary += f"- {f.name}\n"
        if f.suffix in ['.yaml', '.json', '.txt']:
            try:
                with open(f, 'r', encoding='utf-8') as h:
                    content += f"\n--- CONTENT OF {f.name} ---\n{h.read()[:5000]}...\n(truncated)"
            except Exception as e:
                content += f"\n[Error reading {f.name}: {e}]"
                
    return summary + content

@mcp.tool()
def profile_target(path: str) -> str:
    """Check file metadata/safety."""
    if not security.validate_path(path): return "Error: Security Violation"
    return str(profiler.profile_target(path))

@mcp.tool()
def scan_code_structure(path: str) -> str:
    """Index code logic to DB."""
    if not security.validate_path(path): return "Error: Security Violation"
    conn = get_db()
    try: return str(canon_scanner.canon_scan(path, conn))
    finally: conn.close()

@mcp.tool()
def run_verification_tests(path: str) -> str:
    """Run pytest on the given path and return a formatted status string.

    Returns:
        str: A string beginning with either:

            * ``">>>PASS<<< "`` followed by ``res["summary"]`` when tests pass, or
            * ``">>>FAIL<<< "`` followed by ``res["full_log"]`` when any test fails.

    The ``summary`` and ``full_log`` values come from ``test_runner.run_tests(path)``.
    The ``>>>PASS<<<`` and ``>>>FAIL<<<`` markers are stable and intended to be
    machine-parseable so tools can reliably detect the overall test outcome.
    """
    if not security.validate_path(path): return "Error: Security Violation"
    res = test_runner.run_tests(path)
    return f">>>PASS<<< {res['summary']}" if res['passed'] else f">>>FAIL<<< {res['full_log']}"

if __name__ == "__main__":
    mcp.run()
