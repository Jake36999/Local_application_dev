import sqlite3
from importlib.machinery import SourceFileLoader
from pathlib import Path

# Load WorkspacePackager from the v2.3 module (filename has a dot, so use SourceFileLoader)
_PACKAGER_PATH = Path(__file__).resolve().parent / "workspace_packager_v2.3.py"
WorkspacePackager = SourceFileLoader("workspace_packager_v23", str(_PACKAGER_PATH)).load_module().WorkspacePackager

def test_shadow_logging():
    print("🕵️  Starting Shadow Observer Test...")
    
    # 1. Setup DB Connection for logging
    conn = sqlite3.connect("project_meta.db")
    cursor = conn.cursor()
    
    def db_logger(event, payload):
        if event == "dependency_detected":
            print(f"   [Shadow Log] Captured Import: {payload['module']}")
            cursor.execute(
                "INSERT INTO dependencies (source_file, module, timestamp) VALUES (?, ?, ?)",
                (payload['source_file'], payload['module'], "TEST_TIME")
            )
            conn.commit()

    # Ensure table exists for the test run
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS dependencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_file TEXT,
            module TEXT,
            timestamp TEXT
        )
        """
    )
    conn.commit()

    # 2. Run the Packager on the 'app' directory
    # This should trigger analyze_python -> callback -> db_logger
    target_dir = Path("./app")
    packager = WorkspacePackager(target_dir, event_callback=db_logger)
    
    # Run in "text" mode just to trigger the scan
    packager.run("text")
    
    # 3. Verify DB
    print("\n--- 🕸️ DEPENDENCY GRAPH ---")
    cursor.execute("SELECT source_file, module FROM dependencies")
    rows = cursor.fetchall()
    for r in rows:
        print(f"File: {r[0]} -> Depends on: {r[1]}")
    
    conn.close()

if __name__ == "__main__":
    test_shadow_logging()