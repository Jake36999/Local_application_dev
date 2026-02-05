import subprocess
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

def run_tests(target_path: str) -> Dict[str, Any]:
    """
    Executes pytest on a specific file or directory.
    Returns: { "passed": bool, "output": str, "error": str }
    """
    path = Path(target_path)
    if not path.exists():
        return {"passed": False, "output": "", "error": f"Path not found: {target_path}"}

    try:
        # Run pytest in a subprocess
        result = subprocess.run(
            ["pytest", str(path), "-v"],
            capture_output=True,
            text=True,
            timeout=60  # Prevent infinite loops
        )
        
        passed = result.returncode == 0
        output = result.stdout + "\n" + result.stderr
        
        # Heuristic: If we see "failed" in output but returncode is 0, treat as fail
        if "failed" in result.stdout and not passed:
            passed = False

        return {
            "passed": passed,
            "summary": _extract_summary(output),
            "full_log": output[:2000]  # Truncate for LLM context window
        }
    except Exception as e:
        return {"passed": False, "error": str(e)}

def _extract_summary(log: str) -> str:
    """Helper to grab the last line of pytest output (e.g., '3 passed in 0.12s')."""
    lines = log.strip().splitlines()
    if lines:
        return lines[-1]
    return "No summary available"