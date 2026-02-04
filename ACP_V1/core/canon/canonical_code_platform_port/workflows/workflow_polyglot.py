"""Polyglot ingest dispatcher for Canonical Code Platform.

- Python files are forwarded to the existing workflow_ingest pipeline.
- Other text-based assets (ts/tsx/js/jsx/json/md/css/html and similar) are
  registered as FILE_ASSET entries so they appear in the database without
  Python-specific parsing.
"""

import argparse
import hashlib
import os
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

REPO_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = REPO_ROOT / "canon.db"
SUPPORTED_GLOBS = ["*.py", "*.ts", "*.tsx", "*.js", "*.jsx", "*.json", "*.md", "*.css", "*.html"]


def ensure_db() -> sqlite3.Connection:
    """Open a connection; initialize schema if the db is missing."""
    if not DB_PATH.exists():
        try:
            from canon_db import init_db

            init_db(str(DB_PATH))
        except Exception:
            # Fallback to a bare connection; downstream INSERTs will fail if schema is absent.
            DB_PATH.touch()
    return sqlite3.connect(DB_PATH)


def upsert_text_asset(path_obj: Path) -> None:
    """Store a non-Python file as a generic FILE_ASSET component."""
    content = path_obj.read_bytes()
    raw_hash = hashlib.sha256(content).hexdigest()
    line_count = max(1, len(content.splitlines()))
    now = datetime.utcnow().isoformat()
    file_id = str(path_obj)

    with ensure_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO canon_files (
                file_id, repo_path, encoding, newline_style,
                raw_hash_sha256, ast_hash_sha256, byte_size, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(file_id) DO UPDATE SET
                repo_path=excluded.repo_path,
                raw_hash_sha256=excluded.raw_hash_sha256,
                ast_hash_sha256=excluded.ast_hash_sha256,
                byte_size=excluded.byte_size,
                created_at=excluded.created_at
            """,
            (
                file_id,
                str(path_obj),
                "utf-8",
                "unknown",
                raw_hash,
                raw_hash,
                len(content),
                now,
            ),
        )

        component_id = f"{file_id}::asset"
        cur.execute(
            """
            INSERT INTO canon_components (
                component_id, file_id, parent_id, kind, name,
                qualified_name, order_index, nesting_depth,
                start_line, end_line, source_hash, committed_hash, committed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(component_id) DO UPDATE SET
                file_id=excluded.file_id,
                kind=excluded.kind,
                name=excluded.name,
                qualified_name=excluded.qualified_name,
                start_line=excluded.start_line,
                end_line=excluded.end_line,
                source_hash=excluded.source_hash
            """,
            (
                component_id,
                file_id,
                None,
                "FILE_ASSET",
                path_obj.name,
                path_obj.name,
                0,
                0,
                1,
                line_count,
                raw_hash,
                None,
                None,
            ),
        )
        conn.commit()

    print(f"Stored asset: {path_obj}")


def dispatch_python(path_obj: Path) -> int:
    """Delegate Python files to the full ingestion workflow."""
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{REPO_ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}".rstrip(os.pathsep)
    env["PYTHONIOENCODING"] = "utf-8"
    cmd = [sys.executable, str(REPO_ROOT / "workflows" / "workflow_ingest.py"), str(path_obj)]
    print(f"Python ingest: {path_obj}")
    result = subprocess.run(cmd, env=env, cwd=str(REPO_ROOT))
    return result.returncode


def collect_targets(target: Path) -> List[Path]:
    if target.is_file():
        return [target]
    files: set[Path] = set()
    for pattern in SUPPORTED_GLOBS:
        files.update(target.rglob(pattern))
    return sorted(files)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Polyglot ingest dispatcher")
    parser.add_argument("path", help="File or directory to ingest")
    args = parser.parse_args(list(argv) if argv is not None else None)

    target = Path(args.path).expanduser().resolve()
    if not target.exists():
        print(f"Path not found: {target}")
        return 1

    targets = collect_targets(target)
    if not targets:
        print("No supported files found (py, ts, tsx, js, jsx, json, md, css, html).")
        return 0

    failures = 0
    for path_obj in targets:
        if path_obj.suffix.lower() == ".py":
            rc = dispatch_python(path_obj)
            failures += int(rc != 0)
        else:
            try:
                upsert_text_asset(path_obj)
            except Exception as exc:  # pragma: no cover - defensive
                failures += 1
                print(f"Failed asset ingest for {path_obj}: {exc}")

    if failures:
        print(f"Completed with {failures} failure(s).")
        return 1

    print(f"Completed. Ingested {len(targets)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
