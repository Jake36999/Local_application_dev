import shutil
import os
from pathlib import Path

# Configuration
ROOT = Path.cwd()
DEST_DIR = ROOT / "config"
DEST_SETTINGS = DEST_DIR / "settings.py"
DEST_INIT = DEST_DIR / "__init__.py"

# Possible locations where the settings file might be hiding
SOURCES = [
    ROOT / "tooling/ingest/Rag_Ingest_Pipeline/config/settings.py",
    ROOT / "tools/ingest/config/settings.py",
    ROOT / "tools/common/settings.py",
    ROOT / "discovered_assets/tooling/ingest/Rag_Ingest_Pipeline/config/settings.py"
]

def fix_configuration():
    print("🔧 Starting Configuration Repair...")
    
    # 1. Find the source settings file
    source_path = None
    for path in SOURCES:
        if path.exists():
            source_path = path
            print(f"✅ Found settings source: {path}")
            break
    
    # 2. Ensure config directory exists
    DEST_DIR.mkdir(parents=True, exist_ok=True)

    if source_path:
        try:
            shutil.copy(source_path, DEST_SETTINGS)
            print(f"✅ Restored settings to: {DEST_SETTINGS}")
        except Exception as e:
            print(f"❌ Error copying settings: {e}")
    else:
        # Fallback: Create a default settings file if source is lost
        print("⚠️ Source not found. Creating default settings.py...")
        with open(DEST_SETTINGS, "w") as f:
            f.write("import os\n\nsettings = {\n    'log_level': 'INFO',\n    'app_name': 'ACP_v2'\n}\n")
        print(f"✅ Created default settings at: {DEST_SETTINGS}")

    # 3. Create __init__.py (Makes 'config' a valid Python package)
    if not DEST_INIT.exists():
        DEST_INIT.touch()
        print(f"✅ Created package marker: {DEST_INIT}")

    print("\n🎉 Repair Complete. You can now run the Orchestrator.")

if __name__ == "__main__":
    fix_configuration()
