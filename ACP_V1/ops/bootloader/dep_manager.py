import os
import shutil
import logging
import subprocess
from pathlib import Path
from typing import Dict

logger = logging.getLogger("acp.bootloader.deps")

class DependencyManager:
    def __init__(self, root_path: Path):
        self.root = root_path

    def check_system_binaries(self) -> Dict[str, bool]:
        """Checks if external tools are reachable in PATH or common locations."""
        binaries = {
            "git": ["git"],
            "tesseract": [
                "tesseract",
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
            ],
            "python": ["python"]
        }
        status = {}
        for name, candidates in binaries.items():
            found = False
            for candidate in candidates:
                # 1. Check PATH
                if shutil.which(candidate):
                    found = True
                    break
                # 2. Check File Existence (Robust)
                try:
                    p = Path(candidate)
                    if p.exists() and p.is_file():
                        found = True
                        break
                except Exception:
                    continue
            status[name] = found
            if not found:
                logger.warning(f"Missing System Binary: {name}")
        return status

    def consolidate_requirements(self) -> str:
        """
        Scans all subdirectories for requirements.txt, merges them,
        and writes a master file to the root.
        """
        master_reqs = set()
        req_files = list(self.root.rglob("requirements.txt"))
        
        logger.info(f"Found {len(req_files)} requirements files.")

        for req_file in req_files:
            if req_file.name == "requirements_master.txt":
                continue
            if "archive" in str(req_file) or "legacy" in str(req_file):
                continue
                
            try:
                content = req_file.read_text(encoding='utf-8').splitlines()
                for line in content:
                    clean_line = line.strip()
                    if clean_line and not clean_line.startswith("#"):
                        master_reqs.add(clean_line)
            except Exception as e:
                logger.error(f"Failed to read {req_file}: {e}")

        master_path = self.root / "requirements_master.txt"
        sorted_reqs = sorted(list(master_reqs))
        
        try:
            master_path.write_text("\n".join(sorted_reqs), encoding='utf-8')
            return f"Consolidated {len(sorted_reqs)} packages into {master_path.name}"
        except Exception as e:
            logger.error(f"Failed to write master requirements: {e}")
            return f"Error: {str(e)}"