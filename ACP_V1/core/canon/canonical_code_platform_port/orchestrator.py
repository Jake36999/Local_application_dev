"""
Orchestrator - Main Coordinator

Responsibilities:
  1. Monitor staging/incoming/ for new files
  2. Coordinate workflow execution
  3. Manage message bus
  4. Save/load schemas
  5. Provide status to UI
  6. Handle errors and retries
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent
os.environ.setdefault("PYTHONPATH", str(PROJECT_ROOT))
if str(PROJECT_ROOT) not in sys.path:  # keep imports working when launched without PYTHONPATH
    sys.path.insert(0, str(PROJECT_ROOT))

from bus.message_bus import MessageBus


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("Orchestrator")


DEFAULT_CONFIG = {
    "staging": {
        "enabled": True,
        "incoming_dir": "staging/incoming/",
        "processed_dir": "staging/processed/",
        "failed_dir": "staging/failed/",
        "scan_interval_seconds": 5,
        "retention_days": 30,
        "auto_cleanup": True,
    },
    "workflows": {
        "auto_run": ["ingest", "cut_analysis", "governance"],
        "max_concurrent": 3,
        "timeout_seconds": 300,
    },
    "ui": {"enabled": True, "port": 8501},
    "logging": {"level": "INFO", "log_file": "orchestrator.log"},
}

SUPPORTED_GLOBS = [
    "*.py",
    "*.ts",
    "*.tsx",
    "*.js",
    "*.jsx",
    "*.json",
    "*.md",
    "*.css",
    "*.html",
]


class Orchestrator:
    """Central orchestrator managing all components."""

    def __init__(self, config_path: str = "orchestrator_config.json"):
        self.config_path = config_path
        self.config = self._load_config(config_path)
        self.bus = MessageBus()
        self.running = False
        self.scan_thread = None
        self.command_thread = None

        self._init_state()

        logger.info("Orchestrator initialized")

    def _load_config(self, config_path: str) -> Dict:
        """Load orchestrator configuration."""
        config_file = Path(config_path)

        if not config_file.exists():
            self._write_config(config_file, DEFAULT_CONFIG)
            return DEFAULT_CONFIG

        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_config(self, config_file: Path, config: Dict):
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

    def _init_state(self):
        """Initialize orchestrator state."""
        self.bus.set_state("orchestrator_status", "IDLE")
        self.bus.set_state("last_scan", datetime.utcnow().isoformat())
        self.bus.set_state("total_scans", 0)
        self.bus.set_state("failed_scans", 0)
        self.bus.set_state("active_workflows", [])

    def start(self):
        """Start orchestrator."""
        logger.info("Starting orchestrator...")

        self.running = True
        self.bus.set_state("orchestrator_status", "RUNNING")

        self._start_staging_monitor()
        self._start_command_worker()
        self._print_status()

    def stop(self):
        """Stop orchestrator."""
        logger.info("Stopping orchestrator...")

        self.running = False
        self.bus.set_state("orchestrator_status", "STOPPED")
        self.bus.close()

        if self.command_thread and self.command_thread.is_alive():
            self.command_thread.join(timeout=1)

        if self.scan_thread and self.scan_thread.is_alive():
            self.scan_thread.join(timeout=1)

        logger.info("Orchestrator stopped")

    def _start_staging_monitor(self):
        """Start monitoring staging/incoming/ for new files."""
        if not self.config["staging"]["enabled"]:
            logger.info("Staging folder monitoring disabled")
            return

        scan_interval = self.config["staging"]["scan_interval_seconds"]

        def monitor():
            while self.running:
                try:
                    self._scan_staging_folder()
                    time.sleep(scan_interval)
                except Exception as e:
                    logger.error(f"Error in staging monitor: {e}")
                    time.sleep(scan_interval)

        self.scan_thread = threading.Thread(target=monitor, daemon=True)
        self.scan_thread.start()

        logger.info(f"Staging monitor started (interval: {scan_interval}s)")

    def _scan_staging_folder(self):
        """Scan staging/incoming/ for new files."""
        incoming_dir = Path(self.config["staging"]["incoming_dir"])

        if not incoming_dir.exists():
            return

        files_set = set()
        for pattern in SUPPORTED_GLOBS:
            files_set.update(incoming_dir.glob(pattern))
        files = sorted(files_set)

        self.bus.set_state("last_scan", datetime.utcnow().isoformat())

        if files:
            logger.info(f"Found {len(files)} files in staging/incoming/")

            for file_path in files:
                self._process_staging_file(file_path)

    def _process_staging_file(self, file_path: Path):
        """Process a file from staging folder."""
        logger.info(f"Processing {file_path.name}...")

        try:
            staged_path = self._move_to_queue_file(file_path)
            command_id = self.bus.send_command(
                command_type="ingest",
                target="workflows.workflow_polyglot",
                payload={"file_path": str(staged_path), "input_method": "staging_folder"},
            )

            self.bus.publish_event(
                event_type="staging_file_detected",
                source="orchestrator",
                payload={"file_path": str(staged_path), "command_id": command_id},
            )

            logger.info(f"Queued {file_path.name} for ingestion")

        except Exception as e:
            logger.error(f"Failed to process {file_path.name}: {e}")

            failed_dir = Path(self.config["staging"]["failed_dir"])
            failed_dir.mkdir(parents=True, exist_ok=True)

            dest = failed_dir / file_path.name
            file_path.rename(dest)

            logger.info(f"Moved to failed: {dest}")

    def _start_command_worker(self):
        """Poll pending commands and execute them."""
        if self.command_thread and self.command_thread.is_alive():
            return

        poll_interval = 1

        def worker():
            while self.running:
                try:
                    pending = self.bus.get_pending_commands()
                    if not pending:
                        time.sleep(poll_interval)
                        continue

                    max_concurrent = self.config["workflows"].get("max_concurrent", 1)
                    for cmd in pending[:max_concurrent]:
                        self._execute_command(cmd)
                except Exception as exc:  # pragma: no cover - defensive loop guard
                    logger.error(f"Error in command worker: {exc}")
                    time.sleep(poll_interval)

        self.command_thread = threading.Thread(target=worker, daemon=True)
        self.command_thread.start()

    def _execute_command(self, cmd: Dict):
        command_id = cmd["command_id"]
        payload = json.loads(cmd.get("payload_json", "{}"))

        self.bus.update_command_status(command_id, "IN_PROGRESS")

        try:
            if cmd["command_type"] == "ingest":
                file_path = Path(payload.get("file_path", ""))
                if not file_path.exists():
                    raise FileNotFoundError(f"Queued file missing: {file_path}")

                result = self._run_ingest_workflow(file_path)

                if result["returncode"] == 0:
                    self.bus.update_command_status(command_id, "COMPLETED", result)
                    self._bump_metrics(success=True)
                else:
                    self.bus.update_command_status(command_id, "FAILED", result)
                    self._bump_metrics(success=False)
                    self._handle_failed_file(file_path)
            else:
                self.bus.update_command_status(
                    command_id,
                    "FAILED",
                    {"error": f"Unsupported command type: {cmd['command_type']}"},
                )
        except Exception as exc:  # pragma: no cover - defensive
            self.bus.update_command_status(command_id, "FAILED", {"error": str(exc)})
            self._bump_metrics(success=False)
            logger.error(f"Command {command_id} failed: {exc}")

    def _run_ingest_workflow(self, file_path: Path) -> Dict[str, str]:
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{PROJECT_ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}".rstrip(os.pathsep)
        env["PYTHONIOENCODING"] = "utf-8"

        polyglot = PROJECT_ROOT / "workflows" / "workflow_polyglot.py"
        target_script = polyglot if polyglot.exists() else PROJECT_ROOT / "workflows" / "workflow_ingest.py"

        cmd = [sys.executable, str(target_script), str(file_path)]
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=str(PROJECT_ROOT))

        return {
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }

    def _bump_metrics(self, success: bool):
        total = self.bus.get_state("total_scans") or 0
        self.bus.set_state("total_scans", int(total) + 1, data_type="integer")

        if not success:
            failed = self.bus.get_state("failed_scans") or 0
            self.bus.set_state("failed_scans", int(failed) + 1, data_type="integer")

    def _handle_failed_file(self, file_path: Path):
        failed_dir = Path(self.config["staging"]["failed_dir"])
        failed_dir.mkdir(parents=True, exist_ok=True)

        dest = failed_dir / file_path.name
        if dest.exists():
            dest = failed_dir / f"{int(time.time() * 1000)}_{file_path.name}"

        try:
            file_path.rename(dest)
        except Exception:
            logger.warning(f"Could not move failed file {file_path}")

    def _move_to_queue_file(self, file_path: Path) -> Path:
        processed_dir = Path(self.config["staging"]["processed_dir"])
        processed_dir.mkdir(parents=True, exist_ok=True)

        dest = processed_dir / f"{int(time.time() * 1000)}_{file_path.name}"
        counter = 0
        while dest.exists():
            counter += 1
            dest = processed_dir / f"{int(time.time() * 1000)}_{counter}_{file_path.name}"

        file_path.rename(dest)
        return dest

    def save_workflow_schema(self, workflow_name: str, definition: Dict) -> str:
        """Save a workflow schema."""
        schema_id = self.bus.save_schema(
            schema_name=workflow_name, schema_type="workflow", definition=definition
        )

        logger.info(f"Saved workflow schema: {workflow_name} (ID: {schema_id})")

        self.bus.publish_event(
            event_type="schema_saved",
            source="orchestrator",
            payload={
                "schema_id": schema_id,
                "schema_name": workflow_name,
                "schema_type": "workflow",
            },
        )

        return schema_id

    def save_config_schema(self, config_name: str, definition: Dict) -> str:
        """Save a configuration schema."""
        schema_id = self.bus.save_schema(
            schema_name=config_name, schema_type="config", definition=definition
        )

        logger.info(f"Saved config schema: {config_name} (ID: {schema_id})")
        return schema_id

    def get_status(self) -> Dict:
        """Get orchestrator status."""
        return {
            "status": self.bus.get_state("orchestrator_status"),
            "last_scan": self.bus.get_state("last_scan"),
            "total_scans": self.bus.get_state("total_scans"),
            "failed_scans": self.bus.get_state("failed_scans"),
            "config": self.config,
            "state": self.bus.get_all_state(),
        }

    def get_event_log(self, limit: int = 50) -> List[Dict]:
        """Get recent events."""
        return self.bus.get_events(limit=limit)

    def get_pending_commands(self) -> List[Dict]:
        """Get pending commands."""
        return self.bus.get_pending_commands()

    def list_saved_schemas(self, schema_type: Optional[str] = None) -> List[Dict]:
        """List saved schemas."""
        return self.bus.list_schemas(schema_type=schema_type)

    def _print_status(self):
        """Print orchestrator status."""
        status = self.get_status()

        print("\n" + "=" * 70)
        print("ORCHESTRATOR STATUS")
        print("=" * 70)
        print(f"\nStatus: {status['status']}")
        print(f"Last Scan: {status['last_scan']}")
        print(f"Total Scans: {status['total_scans']}")
        print(f"Failed Scans: {status['failed_scans']}")
        print("\nConfiguration:")
        print(f"  - Staging: {status['config']['staging']['enabled']}")
        print(
            f"  - Scan Interval: {status['config']['staging']['scan_interval_seconds']}s"
        )
        print(f"  - Auto Cleanup: {status['config']['staging']['auto_cleanup']}")
        print("\n" + "=" * 70 + "\n")


def init_config_only(config_path: str) -> int:
    config_file = Path(config_path)
    if config_file.exists():
        print("Config already exists.")
        return 0
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)
    print(f"Config created: {config_file}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Canonical Orchestrator")
    parser.add_argument(
        "--init",
        action="store_true",
        help="Create default orchestrator_config.json and exit",
    )
    parser.add_argument(
        "--config",
        default="orchestrator_config.json",
        help="Path to orchestrator config file",
    )
    args = parser.parse_args()

    if args.init:
        raise SystemExit(init_config_only(args.config))

    orchestrator = Orchestrator(config_path=args.config)

    try:
        orchestrator.start()
        while orchestrator.running:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    finally:
        orchestrator.stop()


if __name__ == "__main__":
    main()
