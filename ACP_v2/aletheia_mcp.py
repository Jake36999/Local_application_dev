from mcp.server.fastmcp import FastMCP
import sys
import os
from pathlib import Path
import logging
from typing import Any, Optional

# --- 1. PATH SETUP ---
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- 2. Initialize MCP ---
mcp = FastMCP("Aletheia Agentic Tools")

# --- 3. TOOLS ---

@mcp.tool()
def read_file(path: str) -> str:
    """
    Reads the full content of a file from the codebase.
    Use this to inspect code before making changes.
    Args:
        path: Relative path to the file (e.g., 'config/settings.py')
    """
    try:
        target_path = (Path(ROOT_DIR) / path).resolve()
        # Security check: Ensure we stay inside the project
        if not str(target_path).startswith(str(ROOT_DIR)):
            return "Error: Access denied (Path Traversal)."
        
        if not target_path.exists():
            return f"Error: File not found at {path}"
            
        return target_path.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
def write_file(path: str, content: str) -> str:
    """
    Overwrites (or creates) a file with new content.
    Use this to apply code fixes or create new modules.
    Args:
        path: Relative path to the file.
        content: The full content to write.
    """
    try:
        target_path = (Path(ROOT_DIR) / path).resolve()
        if not str(target_path).startswith(str(ROOT_DIR)):
            return "Error: Access denied (Path Traversal)."
        
        # Ensure directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        target_path.write_text(content, encoding='utf-8')
        return f"Successfully wrote {len(content)} bytes to {path}."
    except Exception as e:
        return f"Error writing file: {str(e)}"

@mcp.tool()
def list_directory(path: str = ".") -> str:
    """Lists files and folders in a directory."""
    try:
        target_path = (Path(ROOT_DIR) / path).resolve()
        if not target_path.exists():
            return "Error: Directory not found."
            
        items = []
        for item in target_path.iterdir():
            if item.name.startswith(('.', '__')): continue # Skip hidden/cache
            kind = "DIR " if item.is_dir() else "FILE"
            items.append(f"[{kind}] {item.name}")
        
        return "\n".join(sorted(items))
    except Exception as e:
        return f"Error listing directory: {str(e)}"

@mcp.tool()
def activate_workflow(name: str, args: Optional[dict[str, Any]] = None) -> str:
    """
    Activates a workflow in the workflows directory by name.
    Args:
        name: Workflow module name (e.g., 'workflow_ingest')
        args: Arguments to pass to workflow (optional)
    """
    import importlib
    if args is None:
        args = {}
    try:
        wf_mod = importlib.import_module(f"workflows.{name}")
        # Try to find a class or function to run
        if hasattr(wf_mod, "IngestionWorkflow"):
            target = args.get("target_path", ".")
            wf = wf_mod.IngestionWorkflow(target)
            results = wf.run()
            return f"Workflow '{name}' completed. Results:\n{results}"
        elif hasattr(wf_mod, "run"):
            return str(wf_mod.run(**args))
        else:
            return f"Workflow '{name}' has no known entry point."
    except Exception as e:
        return f"Error activating workflow '{name}': {str(e)}"

if __name__ == "__main__":
    mcp.run()