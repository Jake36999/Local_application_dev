import os
import shutil
import sys

def purge_legacy():
    # --- 1. SAFETY CHECK ---
    # We enforce that the script MUST run inside 'Local_application_dev\ACP_V1'
    current_path = os.getcwd()
    required_part = os.path.join("Local_application_dev", "ACP_V1")
    
    # Normalize paths to handle slash differences (Windows vs Linux)
    if required_part.lower() not in current_path.lower():
        print("\n⛔ SAFETY STOP TRIGGERED ⛔")
        print(f"Expected path segment: '{required_part}'")
        print(f"Current location:      '{current_path}'")
        print("ACTION ABORTED: Please cd into 'ACP_V1' and run this again.")
        return

    print(f"✅ Safety Verified. Working in: {current_path}")
    print("🔥 STARTING SURGICAL PURGE OF LEGACY FOLDERS...")

    # --- 2. THE KILL LIST ---
    zombies = [
        "canonical_code_platform_port",
        "control_hub_port",
        "directory_bundler_port",
        "Ingest_pipeline_V4r",
        "workspace_creator",
        "Workspace_packager_LLM_construct",
        "bundler_scans",
        "scripts",
        "Context_State"
    ]

    # --- 3. EXECUTE PURGE ---
    for z in zombies:
        target = os.path.join(current_path, z)
        if os.path.exists(target):
            print(f"⚰️  Deleting: {z}...", end=" ")
            try:
                if os.path.isdir(target):
                    shutil.rmtree(target) # Recursive delete
                else:
                    os.remove(target)
                print("DONE.")
            except Exception as e:
                print(f"FAILED ({e})")
                print(f"   ⚠️  Warning: Close any apps using this folder.")
        else:
            print(f"   (Already clean: {z})")

    # --- 4. CLEANUP ORPHANS ---
    # Move loose test files to the proper test directory
    orphans = {
        "test_deep_scan.py": "tests/verification",
        "test_shadow_observer.py": "tests/verification"
    }
    
    # Ensure destination exists
    tests_dir = os.path.join(current_path, "tests", "verification")
    os.makedirs(tests_dir, exist_ok=True)

    for file, dest_subfolder in orphans.items():
        if os.path.exists(file):
            print(f"📦 Moving {file} to tests/verification")
            try:
                shutil.move(file, os.path.join(tests_dir, file))
            except Exception:
                pass # Ignore if already exists

    # --- 5. CLEANUP DUPLICATE DB ---
    # Only delete root DB if the proper one exists in memory/sql
    root_db = "project_meta.db"
    proper_db = os.path.join("memory", "sql", "project_meta.db")
    
    if os.path.exists(root_db) and os.path.exists(proper_db):
        print("🧹 Removing duplicate root database (project_meta.db).")
        try:
            os.remove(root_db)
        except:
            print("   ⚠️  Could not delete DB (it might be open). Skipping.")

    print("\n✨ CLEANUP COMPLETE. Your directory is now clean.")

if __name__ == "__main__":
    purge_legacy()