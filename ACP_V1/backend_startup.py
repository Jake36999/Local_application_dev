import yaml
import shutil
import os
import subprocess
import requests
import json
import time
import glob
from pathlib import Path

# Run requirements consolidation script at startup
import sys
import runpy

# Consolidate requirements before backend startup
try:
    runpy.run_path(str(Path(__file__).parent / "scripts" / "consolidate_requirements.py"))
except Exception as e:
    print(f"[WARN] Could not consolidate requirements: {e}")

# Load Config
CONFIG_PATH = "startup_config.yaml"
if not os.path.exists(CONFIG_PATH):
    print(f"❌ Config not found: {CONFIG_PATH}")
    exit(1)

with open(CONFIG_PATH, "r") as f:
    CONFIG = yaml.safe_load(f)

LOG_FILE = CONFIG["output"]["log_file"]

def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {msg}"
    print(entry)
    with open(LOG_FILE, "a", encoding='utf-8') as f:
        f.write(entry + "\n")

class BackendOrchestrator:
    def __init__(self):
        self.root = Path(CONFIG["paths"]["root"]).resolve()
        self.active_dir = self.root / CONFIG["paths"]["active_context"]
        self.archive_dir = self.root / CONFIG["paths"]["archive_context"]
        self.scan_dir = self.root / CONFIG["paths"]["scan_output_dir"]

    def step_1_cleanup(self):
        log("--- STEP 1: PERCEPTION CLEANUP ---")
        # Ensure directories exist
        self.active_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        files = list(self.active_dir.glob("*"))
        if files:
            print(f"⚠️ Found {len(files)} items in Active Context (Previous Session).")
            # Auto-archive for safety, or ask user. 
            # For automation, we'll archive by default.
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            archive_folder = self.archive_dir / f"session_{timestamp}"
            archive_folder.mkdir()
            
            for f in files:
                shutil.move(str(f), str(archive_folder / f.name))
            log(f"✅ Archived previous context to {archive_folder.name}")
        else:
            log("✅ Active context is clean.")

    def step_2_scan_workspace(self):
        log("--- STEP 2: COLLECTING WORKSPACE INFORMATION ---")
        tool_path = self.root / CONFIG["paths"]["tools"]["bundler"]
        
        # We run the bundler in 'headless' or 'cli' mode if available
        # Assuming arguments: python script.py [target]
        cmd = f'python "{tool_path}" "{self.root}"'
        
        try:
            log(f"   > Running Directory Bundler...")
            subprocess.run(cmd, shell=True, check=True, cwd=self.root)
            log("✅ Scan Complete.")
        except subprocess.CalledProcessError as e:
            log(f"❌ Scan Failed: {e}")
            raise

    def step_3_ingest_memory(self):
        log("--- STEP 3: HYDRATING MEMORY (RAG) ---")
        
        # 1. Identify the latest scan
        if not self.scan_dir.exists():
            log(f"❌ Scan output directory missing: {self.scan_dir}")
            return

        # Find newest folder in bundler_scans
        scans = [d for d in self.scan_dir.iterdir() if d.is_dir()]
        if not scans:
            log("❌ No scan data found.")
            return
            
        latest_scan = max(scans, key=os.path.getmtime)
        log(f"   > Detected latest scan: {latest_scan.name}")

        # 2. Run Hydration Script (The Bridge)
        # We assume hydrate_memory.py is in root
        cmd = f'python hydrate_memory.py "{latest_scan}"'
        try:
            subprocess.run(cmd, shell=True, check=True, cwd=self.root)
            log("✅ Memory Hydration Complete.")
        except subprocess.CalledProcessError as e:
            log(f"❌ Hydration Failed: {e}")

        # 3. Move High-Order Snapshot to Active Context
        # Check for summary YAML in the scan folder
        yaml_files = list(latest_scan.glob("*.yaml"))
        if not yaml_files:
            # Fallback to json if yaml not found
            yaml_files = list(latest_scan.glob("*.json"))
            
        if yaml_files:
            target_file = yaml_files[0] # Take the first report found
            shutil.copy(str(target_file), str(self.active_dir / "current_system_state.yaml"))
            log(f"✅ Moved {target_file.name} to Active Context (Perception Layer)")

    def step_4_verify_llm(self):
        log("--- STEP 4: COGNITIVE VERIFICATION ---")
        url = CONFIG["verification"]["lm_studio_url"]
        
        try:
            # Simple ping
            requests.get(url.replace("/chat/completions", "/models"), timeout=2)
        except:
            log("❌ LM Studio Connection Refused. Please start the server on Port 1234.")
            return

        results = []
        for i, prompt in enumerate(CONFIG["verification"]["test_prompts"]):
            log(f"   > Test {i+1}: {prompt[:30]}...")
            payload = {
                "messages": [
                    {"role": "system", "content": "You are Aletheia. Be concise."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1
            }
            try:
                resp = requests.post(url, json=payload).json()
                answer = resp['choices'][0]['message']['content']
                results.append({"prompt": prompt, "answer": answer})
                log(f"     [Reply]: {answer[:60]}...")
            except Exception as e:
                log(f"     ❌ Error: {e}")

        # Log verification for the Watcher
        with open(self.active_dir / "verification_log.json", "w") as f:
            json.dump(results, f, indent=2)

    def run(self):
        print("\n🚀 INITIALIZING ALETHEIA BACKEND...\n")
        try:
            self.step_1_cleanup()
            self.step_2_scan_workspace()
            self.step_3_ingest_memory()
            self.step_4_verify_llm()
            
            # Final Signal
            with open(CONFIG["output"]["bus_signal"], "w") as f:
                json.dump({"status": "READY", "timestamp": time.time()}, f)
                
            print("\n✨ SYSTEM READY. Bus Signal Emitted. ✨")
        except Exception as e:
            print(f"\n💥 CRITICAL FAILURE: {e}")
            log(f"CRITICAL FAILURE: {e}")

if __name__ == "__main__":
    orchestrator = BackendOrchestrator()
    orchestrator.run()
