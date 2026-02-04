import os
import json

# 1. DEFINE THE NEW CONTENTS
# ---------------------------------------------------------

# The Updated LM Studio JSON Configuration
# Points to the Local_application_dev root
lm_studio_config = {
    "mcpServers": {
        "aletheia": {
            "command": "python",
            "args": [
                "C:/Users/jakem/Documents/Aletheia_project/Local_application_dev/aletheia_mcp.py"
            ],
            "env": {
                "PYTHONPATH": "C:/Users/jakem/Documents/Aletheia_project/Local_application_dev"
            }
        }
    }
}

# The Updated MCP Python Script
# Contains the Factory Manager logic and Perception Root check
mcp_script_content = r"""from mcp.server.fastmcp import FastMCP
import sqlite3
import sys
import os
from pathlib import Path
import glob

# Ensure we can import from 'core' if it exists in this directory
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "core"))

# Try importing tools. If 'core' was migrated to ACP_V1, you may need to adjust this path
# e.g., sys.path.append("./ACP_V1") and from tooling...
try:
    from tools import profiler, security, canon_scanner, pdf_scanner, test_runner
except ImportError:
    # Fallback/Placeholder if imports fail due to migration
    print("⚠️ Warning: Could not import 'tools'. Check if 'core' folder exists or was migrated.")
    class MockTool:
        def profile_target(self, p): return "Tool Missing"
        def canon_scan(self, p, c): return "Tool Missing"
        def run_tests(self, p): return {"passed": False, "full_log": "Tool Missing"}
    profiler = security = canon_scanner = pdf_scanner = test_runner = MockTool()
    security.validate_path = lambda p: True

# Initialize
mcp = FastMCP("Aletheia Factory Manager")

def get_db():
    return sqlite3.connect("project_meta.db", check_same_thread=False)

@mcp.tool()
def read_system_state() -> str:
    """
    Retrieves the OFFICIAL system state.
    Restricted to the 'Active' context folder.
    """
    """
    """
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
    """Run pytest. Returns >>>PASS<<< or >>>FAIL<<<."""
    if not security.validate_path(path): return "Error: Security Violation"
    res = test_runner.run_tests(path)
    return f">>>PASS<<< {res['summary']}" if res['passed'] else f">>>FAIL<<< {res['full_log']}"

if __name__ == "__main__":
    mcp.run()
"""

# 2. WRITE THE FILES
# ---------------------------------------------------------

# Write aletheia_mcp.py
with open("aletheia_mcp.py", "w", encoding="utf-8") as f:
    f.write(mcp_script_content)
print("✅ Updated: aletheia_mcp.py")

# Write LM Studio Config (for easy copy-pasting)
with open("lms_config.json", "w", encoding="utf-8") as f:
    json.dump(lm_studio_config, f, indent=2)
print("✅ Created: lms_config.json")

print("\n👇 ACTION REQUIRED:")
print("1. Open 'lms_config.json' and copy the content.")
print("2. Paste it into your LM Studio 'Developer' > 'MCP' configuration.")
print("3. Restart the MCP server in LM Studio.")