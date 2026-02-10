import os
import sys
import yaml
from pathlib import Path
from datetime import datetime

# --- Import Core Utils ---
sys.path.append(os.path.abspath("ACP_V1"))
try:
    from core.shared_utils import deploy_bundle, sanitize_filename
except ImportError:
    print("❌ Critical Error: Could not import 'ACP_V1/core/shared_utils.py'.")
    print("   Ensure you are running this from the project root.")
    sys.exit(1)

# --- Configuration ---
SOURCE_DIR = Path("ACP_V1")
OUTPUT_DIR = Path("backups") # Where snapshots live
IGNORE_DIRS = {
    "__pycache__", ".git", ".venv", "venv", "node_modules", 
    "Orchestrator_Output", "backups", ".pytest_cache"
}
IGNORE_EXTS = {".pyc", ".pyd", ".log", ".tmp", ".DS_Store"}

def pack_workspace():
    print(f"📦 Packing workspace from: {SOURCE_DIR}")
    
    docs = []
    
    # 1. Create Manifest
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    docs.append({
        "kind": "DeploymentManifest",
        "metadata": {
            "name": f"Snapshot_{timestamp}",
            "author": "WorkspacePackager",
            "timestamp": timestamp
        },
        "spec": {
            "source": str(SOURCE_DIR),
            "type": "FullBackup"
        }
    })

    # 2. Walk and Pack Files
    file_count = 0
    for root, dirs, files in os.walk(SOURCE_DIR):
        # Prune ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if any(file.endswith(ext) for ext in IGNORE_EXTS):
                continue
                
            full_path = Path(root) / file
            rel_path = full_path.relative_to(SOURCE_DIR)
            
            try:
                # Binary check
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    docs.append({
                        "kind": "File",
                        "metadata": {"name": str(rel_path)},
                        "content": content
                    })
                    file_count += 1
                    print(f"   + Packed: {rel_path}")
                    
                except UnicodeDecodeError:
                    print(f"   ⚠️ Skipping binary file: {rel_path}")
                    
            except Exception as e:
                print(f"   ❌ Error reading {rel_path}: {e}")

    # 3. Deploy (Create Snapshot)
    print(f"\n💾 Saving Snapshot...")
    result = deploy_bundle(docs, OUTPUT_DIR)
    
    print("\n" + "="*50)
    print(f"✅ SNAPSHOT COMPLETE: {result['version']}")
    print(f"📂 Location: {result['path']}")
    print(f"📄 Files: {result['file_count']}")
    print("="*50)

if __name__ == "__main__":
    pack_workspace()
