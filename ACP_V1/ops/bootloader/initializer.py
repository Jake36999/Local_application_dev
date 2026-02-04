import os
import sqlite3
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List
import shutil

logger = logging.getLogger("acp.bootloader.init")

class SystemInitializer:
    def __init__(self, root_path: Path):
        self.root = root_path

    def check_environment(self) -> Dict[str, Any]:
        """Validates Python version and critical env vars."""
        return {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
            "compatible": sys.version_info >= (3, 10),
            "cwd": str(os.getcwd())
        }

    def scaffold_directories(self) -> List[str]:
        """Idempotently creates the required folder structure."""
        required_dirs = [
            "tooling/common",
            "tooling/bundler",
            "tooling/ingest",
            "tooling/analysis",
            "core/canon",
            "core/bus",
            "memory/sql",
            "memory/vector",
            "safe_ops/context/active",
            "safe_ops/context/archive",
            "logs",
            "config"
        ]
        created = []
        for d in required_dirs:
            target = self.root / d
            if not target.exists():
                target.mkdir(parents=True, exist_ok=True)
                created.append(d)
        return created

    def hydrate_databases(self) -> str:
        """Ensures the SQLite DB exists and has the base schema."""
        db_path = self.root / "memory/sql/project_meta.db"
        
        # Ensure parent dir exists
        db_path.parent.mkdir(parents=True, exist_ok=True)

        status = "Existing"
        if not db_path.exists():
            status = "Created"
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            # Basic Schema Definition (Base Truth)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS canon_components (
                    id TEXT PRIMARY KEY,
                    file TEXT,
                    kind TEXT,
                    name TEXT,
                    code_snippet TEXT,
                    hash TEXT
                )
            ''')
            conn.commit()
            conn.close()
            return f"Database {status} and Schema Verified at {db_path.name}"
        except Exception as e:
            logger.error(f"DB Init Failed: {e}")
            raise e

    def clean_context(self) -> int:
        """Hard Clean: Moves active context to archive."""
        active = self.root / "safe_ops/context/active"
        archive = self.root / "safe_ops/context/archive"
        
        count = 0
        if active.exists():
            for item in active.glob("*"):
                try:
                    target = archive / item.name
                    if item.is_dir():
                        shutil.copytree(item, target, dirs_exist_ok=True)
                        shutil.rmtree(item)
                    else:
                        shutil.move(str(item), str(target))
                    count += 1
                except Exception as e:
                    logger.error(f"Failed to archive {item}: {e}")
        return count