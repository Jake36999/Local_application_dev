import shutil
import os
import subprocess
from pathlib import Path

def test_tesseract():
    print("--- Tesseract Detection Utility ---")
    
    # 1. Check System PATH (What the bootloader currently does)
    path_in_env = shutil.which("tesseract")
    if path_in_env:
        print(f"✅ Found in PATH: {path_in_env}")
    else:
        print("❌ Not found in System PATH")

    # 2. Check Explicit Path (Your location)
    known_path = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    if known_path.exists():
        print(f"✅ Found at Known Location: {known_path}")
    else:
        print(f"❌ Not found at: {known_path}")

    # 3. Execution Test
    target = path_in_env if path_in_env else str(known_path)
    if target and os.path.exists(target):
        try:
            result = subprocess.run([target, "--version"], capture_output=True, text=True)
            print(f"\n--- Execution Test ---\n{result.stdout.splitlines()[0]}")
            print("SUCCESS: Tesseract is executable.")
        except Exception as e:
            print(f"FAILURE: Could not run tesseract: {e}")
    else:
        print("\nFAILURE: No valid Tesseract executable found.")

if __name__ == "__main__":
    test_tesseract()