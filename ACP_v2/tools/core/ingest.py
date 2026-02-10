
import sys, ast, hashlib, uuid, datetime, os
from tools.core.canon_db import init_db
from tools.core.canon_extractor import CanonExtractor
from tools.analysis.call_graph_normalizer import CallGraphNormalizer
from tools.analysis.semantic_rebuilder import SemanticRebuilder
from tools.analysis.drift_detector import DriftDetector

def main():
    # 1. Validation: Ensure argument provided
    if len(sys.argv) != 2:
        print("\n[!] Usage Error")
        print("USAGE: python core/ingest.py <path_to_python_file>")
        print("EXAMPLE: python core/ingest.py core/canon_extractor.py\n")
        sys.exit(1)

    path = sys.argv[1]

    # 2. Validation: Ensure file exists
    if not os.path.isfile(path):
        print(f"\n[!] Error: File not found: {path}")
        print("Check the spelling or provide the full path.\n")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        src = f.read()

    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        print(f"\n[!] Syntax Error in {path}:")
        print(f"{e}\n")
        sys.exit(1)

    conn = init_db()
    
    print(f"[*] Ingesting {path}...")
    
    # ===== PHASE 1: Resolve File ID (Stable File Tracking) =====
    existing_file = conn.execute(
        "SELECT file_id FROM canon_files WHERE repo_path=?",
        (path,)
    ).fetchone()
    
    # ===== PHASE 6: Determine version number =====
    if existing_file:
        fid = existing_file[0]
        # Get current version number
        current_version_row = conn.execute(
            "SELECT MAX(version_number) FROM file_versions WHERE file_id=?",
            (fid,)
        ).fetchone()
        next_version = (current_version_row[0] or 0) + 1
        print(f"[*] Updating existing file (ID: {fid}) - Version {next_version}")
        
        # ===== PHASE 2: CAPTURE HISTORY (Discrepancy Fix 1) =====
        # Fetch current committed state BEFORE we delete it
        history_rows = conn.execute(
            "SELECT qualified_name, committed_hash, committed_at FROM canon_components WHERE file_id=?",
            (fid,)
        ).fetchall()
        # Create dictionary: {qualified_name: (committed_hash, committed_at)}
        history = {row[0]: (row[1], row[2]) for row in history_rows}
        
        # ===== PHASE 3: PURGE OLD COMPONENTS (Discrepancy Fix 1) =====
        # Delete old components to prevent duplication
        conn.execute("DELETE FROM canon_components WHERE file_id=?", (fid,))
        conn.execute("DELETE FROM canon_source_segments WHERE component_id NOT IN (SELECT component_id FROM canon_components)")  # Cleanup orphans
        
        # Update file metadata
        conn.execute(
            """
            UPDATE canon_files 
            SET raw_hash_sha256=?, ast_hash_sha256=?, byte_size=?, created_at=?
            WHERE file_id=?
            """,
            (
                hashlib.sha256(src.encode()).hexdigest(),
                hashlib.sha256(ast.dump(tree).encode()).hexdigest(),
                len(src.encode()),
                datetime.datetime.utcnow().isoformat(),
                fid
            )
        )
        conn.commit()
    else:
        fid = str(uuid.uuid4())
        next_version = 1
        history = {}  # No history for new file
        print(f"[*] Registering new file (ID: {fid}) - Version 1")
        
        # Store new file record
        conn.execute(
            "INSERT INTO canon_files VALUES (?,?,?,?,?,?,?,?)",
            (
                fid,
                path,
                "utf-8",
                "LF",
                hashlib.sha256(src.encode()).hexdigest(),
                hashlib.sha256(ast.dump(tree).encode()).hexdigest(),
                len(src.encode()),
                datetime.datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()
    
    # ===== PHASE 6: Create version snapshot BEFORE extraction =====
    version_id = str(uuid.uuid4())
    raw_hash = hashlib.sha256(src.encode()).hexdigest()
    ast_hash = hashlib.sha256(ast.dump(tree).encode()).hexdigest()
    
    # Get previous version ID (for lineage tracking)
    if next_version > 1:
        prev_version_row = conn.execute("""
            SELECT version_id FROM file_versions 
            WHERE file_id=? AND version_number=?
        """, (fid, next_version - 1)).fetchone()
        previous_version_id = prev_version_row[0] if prev_version_row else None
    else:
        previous_version_id = None
    
    conn.execute("""
        INSERT INTO file_versions VALUES (?,?,?,?,?,?,?,?,?)
    """, (
        version_id,
        fid,
        next_version,
        previous_version_id,
        raw_hash,
        ast_hash,
        datetime.datetime.utcnow().isoformat(),
        0,  # component_count (updated later)
        ""   # change_summary (updated by drift detector)
    ))
    conn.commit()
    
    # ===== PHASE 4: Run Extraction with History (Discrepancy Fix 2) =====
    # Pass the history dict so extractor knows what hashes to adopt
    extractor = CanonExtractor(src, fid, conn, history=history)
    extractor.visit(tree)
    
    # ===== PHASE 5: Flush Symbols (Phase 2 Symbol Tracking) =====
    extractor.flush_symbols()
    
    # ===== PHASE 6: Normalize Call Graph (Phase 3) =====
    # This must run after extraction to have all components registered
    print("[*] Normalizing call graph...")
    normalizer = CallGraphNormalizer()
    normalizer.normalize_calls()
    normalizer.compute_metrics()
    normalizer.detect_orchestrators()
    normalizer.build_dependency_dag()
    
    # ===== PHASE 6: Update component count in version record =====
    component_count = conn.execute(
        "SELECT COUNT(*) FROM canon_components WHERE file_id=?", 
        (fid,)
    ).fetchone()[0]
    
    conn.execute("""
        UPDATE file_versions 
        SET component_count=? 
        WHERE version_id=?
    """, (component_count, version_id))
    conn.commit()
    
    # ===== PHASE 6: Run Drift Detection =====
    print("[*] Analyzing drift...")
    detector = DriftDetector(conn)
    drift_stats = detector.detect_drift(fid, version_id)
    
    print(f"[+] Ingest complete.")
    print(f"    File ID: {fid}")
    print(f"    Version: {next_version}")
    print(f"    Components: {component_count}")
    print(f"    Drift: +{drift_stats['added']} -{drift_stats['removed']} ~{drift_stats['modified']}")
    print(f"    Run 'python rebuild_verifier.py' next.")

if __name__ == "__main__":
    main()
