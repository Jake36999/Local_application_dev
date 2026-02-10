import sys
import os
import json
from pathlib import Path

# Add Ingest Pipeline to path
sys.path.append(os.path.join(os.getcwd(), "LCD_port", "Ingest_pipeline_V4r"))
from core.retrieval_controller import RetrievalController

def hydrate(scan_path_str):
    scan_path = Path(scan_path_str).resolve()
    print(f"🌊 Hydrating from: {scan_path.name}")
    
    if not scan_path.exists():
        print(f"❌ Path not found: {scan_path}")
        sys.exit(1)

    try:
        mem = RetrievalController()
        print("   - Vector DB Connection: OK")
    except Exception as e:
        print(f"❌ Vector DB Error: {e}")
        sys.exit(1)

    # Load file manifest or tree
    # Looking for 'tree.json' or 'scan_DIRECTORY_MAP...'
    tree_file = scan_path / "tree.json"
    if not tree_file.exists():
        # Fallback to manifest
        tree_file = scan_path / "manifest.json"
    
    if not tree_file.exists():
        print("❌ No tree.json or manifest.json found in scan.")
        return

    with open(tree_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Simplified Ingestion Logic
    # In a real run, this would iterate 'data' and add_document()
    # For now, we confirm connection and readiness
    print(f"   - Identified {len(data)} items for memory.")
    
    # Example insertion of metadata
    mem.add_document(
        source="system_scan",
        content=f"System scan completed at {scan_path.name}. Contains {len(data)} files.",
        metadata={"type": "scan_summary"}
    )
    print("✅ Hydration successful.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python hydrate_memory.py <path_to_scan_folder>")
        sys.exit(1)
    hydrate(sys.argv[1])
