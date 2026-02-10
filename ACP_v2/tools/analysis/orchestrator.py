
import json
import time
import shutil
import importlib
import sys
from pathlib import Path
from typing import Dict, Callable

# Add root to path for tool imports
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

# Utility logging
def log(msg):
    print(f"[ORCHESTRATOR] {msg}")

class WorkflowRegistry:
    """Maps string names from config to actual Python functions"""
    def __init__(self):
        self.workflows: Dict[str, Callable] = {}

    def register(self, name: str, func: Callable):
        self.workflows[name] = func

    def execute(self, name: str, target_file: Path):
        if name in self.workflows:
            log(f"🚀 Triggering Workflow: {name} on {target_file.name}")
            try:
                # Dynamic execution wrapper
                self.workflows[name](str(target_file))
                return True
            except Exception as e:
                log(f"❌ Workflow {name} Failed: {e}")
                return False
        return False

class BackendOrchestrator:
    def __init__(self):
        self.root = ROOT_DIR
        self.config_path = self.root / "config" / "orchestrator_config.json"
        self.config = self._load_config()
        self.registry = WorkflowRegistry()
        self._setup_directories()
        # --- REGISTER TOOLS HERE ---
        # We will lazy import these to avoid circular dependency crashes on boot
        self._register_default_workflows()

    def _load_config(self):
        if not self.config_path.exists():
            log("⚠️ Config missing, using defaults.")
            return {"staging": {"scan_interval_seconds": 5}}
        with open(self.config_path, "r") as f:
            return json.load(f)

    def _setup_directories(self):
        """Ensure staging folders exist"""
        staging = self.config.get("staging", {})
        self.incoming = self.root / staging.get("incoming_dir", "staging/incoming")
        self.processed = self.root / staging.get("processed_dir", "staging/processed")
        self.failed = self.root / staging.get("failed_dir", "staging/failed")
        
        for p in [self.incoming, self.processed, self.failed]:
            p.mkdir(parents=True, exist_ok=True)


    def _register_default_workflows(self):
        """Map config strings to actual tool functions"""
        # Real workflow registration
        from tools.ingest.ingest_manager import IngestManager
        from tools.analysis.cut_analysis import CutAnalyzer
        from tools.analysis.governance_report import GovernanceReport

        self._ingest_manager = IngestManager()
        self._cut_analyzer = CutAnalyzer()
        self._governance_report = GovernanceReport()

        def ingest_workflow(path):
            log(f"Running real INGEST workflow on {path}")
            return self._ingest_manager.process_file(Path(path))

        def cut_analysis_workflow(path):
            log(f"Running real CUT_ANALYSIS workflow on {path}")
            self._cut_analyzer.analyze()

        def governance_workflow(path):
            log(f"Running real GOVERNANCE workflow on {path}")
            # Write a stub governance report to processed dir
            out_path = self.processed / f"{Path(path).stem}_governance_report.txt"
            self._governance_report.write_report(str(out_path))

        self.registry.register("ingest", ingest_workflow)
        self.registry.register("cut_analysis", cut_analysis_workflow)
        self.registry.register("governance", governance_workflow)

    def process_file(self, file_path: Path):
        """Run all auto_run workflows on a file"""
        workflows = self.config.get("workflows", {}).get("auto_run", [])
        success = True
        
        for wf_name in workflows:
            if not self.registry.execute(wf_name, file_path):
                success = False
                break # Stop chain on failure
        
        # Move file based on outcome
        dest = self.processed if success else self.failed
        shutil.move(str(file_path), str(dest / file_path.name))
        log(f"Moved {file_path.name} to {dest.name}")


    def _write_heartbeat(self, status="Online"):
        """Write a heartbeat status file for API/status checks"""
        heartbeat_path = self.root / "orchestrator.status.json"
        data = {
            "status": status,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        with open(heartbeat_path, "w") as f:
            json.dump(data, f)

    def run_loop(self):
        interval = self.config.get("staging", {}).get("scan_interval_seconds", 5)
        log(f"👀 Watching {self.incoming} (Interval: {interval}s)")
        try:
            while True:
                # Scan for files
                for item in self.incoming.iterdir():
                    if item.is_file():
                        self.process_file(item)
                self._write_heartbeat(status="Online")
                time.sleep(interval)
        except KeyboardInterrupt:
            self._write_heartbeat(status="Offline")
            log("🛑 Orchestrator shutting down.")

if __name__ == "__main__":
    orchestrator = BackendOrchestrator()
    orchestrator.run_loop()
