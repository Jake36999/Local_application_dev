import os
import shutil
from pathlib import Path

def safe_move(src, dest):
    if os.path.exists(src):
        shutil.move(src, dest)
        print(f"✅ Moved {src} -> {dest}")
    else:
        print(f"⚠️  {src} not found (already moved?)")

def safe_delete(filename):
    if os.path.exists(filename):
        os.remove(filename)
        print(f"🗑️  Deleted {filename}")
    else:
        print(f"ℹ️  {filename} already deleted")

print("🧹 Running Final Polish...")

# 1. Move the infrastructure test to the correct folder
safe_move("test_infrastructure.py", "tests/test_infrastructure.py")

# 2. Delete the deprecated root workflows (the real ones are in workflows/)
deprecated_files = [
    "workflow_extract.py", 
    "workflow_ingest.py", 
    "workflow_schema.py", 
    "workflow_verify.py"
]

for f in deprecated_files:
    safe_delete(f)

print("\n✨ Root directory is now clean.")