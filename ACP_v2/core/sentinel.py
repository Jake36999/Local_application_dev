import logging
from typing import Any
import os
import subprocess
from pathlib import Path
from typing import Dict

# Initialize module-level logger
logger = logging.getLogger("Sentinel")

class SentinelGatekeeper:
    """
    Workflow I: The Sentinel Gatekeeper.
    Acts as the mandatory pre-condition validator for the Orchestrator.
    """

    def __init__(self, config: Dict):
        self.config = config
        self.sentinel_cfg = config.get("sentinel", {})
        self.binary_paths = self.sentinel_cfg.get("binary_paths", {})
        self.enforce_typing = self.sentinel_cfg.get("enforce_typing", False)
        self._validated_binaries: Dict[str, Any] = {}

    def validate_environment(self) -> bool:
        """
        Checks if the host environment has the required 'physical' dependencies 
        (Poppler, Tesseract) to handle multimodal ingestion.
        """
        all_passed = True
        
        for name, bin_path in self.binary_paths.items():
            # Cache success to avoid subprocess overhead on every file
            if self._validated_binaries.get(name):
                continue

            path_obj = Path(bin_path)
            if not path_obj.exists():
                logger.error(f"[SENTINEL] FAIL: {name} binary not found at {bin_path}")
                all_passed = False
                continue

            # Optional: Test execution (lightweight)
            try:
                cmd = [str(path_obj), "--version"] if "tesseract" in name.lower() or "pdf" in name.lower() else [str(path_obj), "--help"]
                subprocess.run(cmd, capture_output=True, timeout=2, check=False)
                self._validated_binaries[name] = True
            except Exception as e:
                logger.error(f"[SENTINEL] FAIL: {name} is present but not executable: {e}")
                all_passed = False
        
        return all_passed

    def enforce_structural_hygiene(self, target_path: Path):
        """
        Enforces project structure rules, such as ensuring 'py.typed' exists
        in packages to satisfy VS Code / Pylance strict modes.
        """
        if not self.enforce_typing:
            return

        # If processing a directory or a file within a package structure
        scan_root = target_path if target_path.is_dir() else target_path.parent
        
        for root, dirs, files in os.walk(scan_root):
            if "__init__.py" in files:
                marker = Path(root) / "py.typed"
                if not marker.exists():
                    try:
                        marker.touch()
                        logger.info(f"[SENTINEL] HYGIENE: Created {marker}")
                    except Exception as e:
                        logger.warning(f"[SENTINEL] Could not create py.typed at {root}: {e}")

    def audit_file(self, file_path: Path) -> bool:
        """
        Master gatekeeping method. Returns True if the file is cleared for ingestion.
        """
        # 1. Environmental Check (Binaries)
        if not self.validate_environment():
            return False

        # 2. Structural Hygiene (Side-effect: fixes missing markers)
        self.enforce_structural_hygiene(file_path)

        # 3. Validation Logic (Add specific file checks here if needed)
        if file_path.stat().st_size == 0:
            logger.warning(f"[SENTINEL] REJECT: File is empty {file_path.name}")
            return False

        logger.info(f"[SENTINEL] PASS: {file_path.name} cleared for ingestion.")
        return True
