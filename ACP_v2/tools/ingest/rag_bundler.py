import os
import json
from pathlib import Path
from typing import List, Dict, Any  # Already correct

def create_verification_snapshot(output_name: str = "RAG_System_Deep_Snapshot.json") -> None:
    """
    Scans all project files and their contents for code and telemetry verification.
    Includes logs and config files usually ignored in standard builds.
    """
    # Use explicit type for snapshot
    snapshot: Dict[str, Any] = {
        "project": "RAG Ingestion Pipeline (V4)",
        "purpose": "Code & Telemetry Verification",
        "directory_structure": [],
        "files": []
    }

    # Pruned ignore list: We now WANT to see logs and env files
    ignore_dirs = {'__pycache__', '.vs', '.git', '.idea', 'venv', 'env'}
    # Only skip actual heavy binaries that can't be read as text
    binary_extensions = {'.pyc', '.exe', '.dll', '.lib', '.pdf', '.zip', '.sqlite', '.h5'}

    base_dir = Path(__file__).parent.resolve()
    print(f"--- Initiating Deep Verification Scan ---")
    print(f"Scanning: {base_dir}")

    file_count = 0
    
    for root, dirs, files in os.walk(base_dir):
        # Prune basic system dirs
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        relative_root = Path(root).relative_to(base_dir)
        depth = len(relative_root.parts)
        indent = "  " * depth
        
        if root != str(base_dir):
            snapshot["directory_structure"].append(f"{indent}[DIR] {relative_root.as_posix()}")

        for file in files:
            path = Path(root) / file
            rel_path = path.relative_to(base_dir).as_posix()
            
            # Map the structure
            file_indent = "  " * (depth + 1)
            snapshot["directory_structure"].append(f"{file_indent}[FILE] {file}")

            # Skip binaries, but read everything else (logs, env, py, json)
            if path.suffix.lower() in binary_extensions or file == output_name:
                continue
                
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Determine module or category
                parts = Path(rel_path).parts
                category = parts[0] if len(parts) > 1 else "root"

                print(f"Indexing for Verification: {rel_path}")

                snapshot["files"].append({
                    "path": rel_path,
                    "category": category,
                    "content": content,
                    "size_chars": len(content)
                })
                file_count += 1
                
            except Exception as e:
                print(f"Could not read {rel_path}: {e}")

    # Save the exhaustive snapshot
    try:
        output_path = base_dir / output_name
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2)
        print(f"\n--- Scan Complete ---")
        print(f"Verification file created: {output_path}")
        print(f"Total source/log files captured: {file_count}")
    except Exception as e:
        print(f"Critical error writing snapshot: {e}")

if __name__ == "__main__":
    create_verification_snapshot()