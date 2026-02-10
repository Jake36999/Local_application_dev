#!/usr/bin/env python3
"""Phase 4 verification: prove DB AST == disk AST for latest file."""

import ast
import hashlib
import sys
import uuid
import datetime
from pathlib import Path

from core.canon_db import init_db


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def main() -> int:
    print("\n" + "=" * 60)
    print("PHASE 4: SYSTEM VERIFICATION")
    print("=" * 60)

    conn = init_db()
    c = conn.cursor()

    candidates = c.execute(
        """
        SELECT file_id, repo_path, ast_hash_sha256
        FROM canon_files
        ORDER BY created_at DESC
        LIMIT 50
        """
    ).fetchall()

    if not candidates:
        print("[!] No files found. Run ingest first.")
        return 1

    rec = None
    for row in candidates:
        fid, repo_path, ast_hash = row
        if Path(repo_path).exists():
            rec = row
            break

    if not rec:
        print("[!] No candidate files exist on disk. Ingest a file and retry.")
        return 1

    file_id, path, stored_ast_hash = rec
    print(f"[*] Verifying: {path}")

    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    current_raw_hash = sha256(source)

    try:
        tree = ast.parse(source)
        current_ast_hash = sha256(ast.dump(tree, include_attributes=False))
    except SyntaxError:
        print("[!] Syntax error in source; cannot verify.")
        return 1

    match = current_ast_hash == stored_ast_hash
    status = "VERIFIED" if match else "DRIFT_DETECTED"

    print(f"    Stored AST Hash : {stored_ast_hash[:16]}...")
    print(f"    Current AST Hash: {current_ast_hash[:16]}...")
    print(f"    Raw Hash        : {current_raw_hash[:16]}...")

    if match:
        print("\n[SUCCESS] Integrity confirmed: DB matches disk.")
    else:
        print("\n[WARNING] Integrity check failed: drift detected.")

    proof_id = str(uuid.uuid4())
    c.execute(
        """
        INSERT INTO equivalence_proofs
        (proof_id, file_id, original_ast_hash, rebuilt_ast_hash,
         ast_match, semantic_equivalent, proof_status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            proof_id,
            file_id,
            stored_ast_hash,
            current_ast_hash,
            1 if match else 0,
            1 if match else 0,
            status,
            datetime.datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    print(f"[*] Proof logged: {proof_id[:8]}")

    return 0 if match else 2


if __name__ == "__main__":
    sys.exit(main())
