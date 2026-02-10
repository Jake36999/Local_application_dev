
import sqlite3

def init_db(db_path="canon.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS canon_files (
        file_id TEXT PRIMARY KEY,
        repo_path TEXT,
        encoding TEXT,
        newline_style TEXT,
        raw_hash_sha256 TEXT,
        ast_hash_sha256 TEXT,
        byte_size INTEGER,
        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS canon_components (
        component_id TEXT PRIMARY KEY,
        file_id TEXT,
        parent_id TEXT,
        kind TEXT,
        name TEXT,
        qualified_name TEXT,
        order_index INTEGER,
        nesting_depth INTEGER,
        start_line INTEGER,
        end_line INTEGER,
        source_hash TEXT,
        committed_hash TEXT,
        committed_at TEXT
    );

    CREATE TABLE IF NOT EXISTS canon_source_segments (
        component_id TEXT PRIMARY KEY,
        source_text TEXT
    );

    CREATE TABLE IF NOT EXISTS canon_symbols (
        symbol_id TEXT PRIMARY KEY,
        component_id TEXT,
        name TEXT,
        symbol_kind TEXT
    );

    CREATE TABLE IF NOT EXISTS canon_imports (
        import_id TEXT PRIMARY KEY,
        component_id TEXT,
        module TEXT,
        name TEXT,
        alias TEXT
    );

    CREATE TABLE IF NOT EXISTS canon_calls (
        call_id TEXT PRIMARY KEY,
        component_id TEXT,
        call_target TEXT,
        lineno INTEGER
    );

    CREATE TABLE IF NOT EXISTS canon_globals (
        global_id TEXT PRIMARY KEY,
        component_id TEXT,
        name TEXT,
        access_type TEXT
    );

    CREATE TABLE IF NOT EXISTS audit_rebuild_events (
        rebuild_id TEXT PRIMARY KEY,
        file_id TEXT,
        raw_hash_match INTEGER,
        ast_hash_match INTEGER,
        status TEXT,
        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS overlay_semantic (
        overlay_id TEXT PRIMARY KEY,
        target_id TEXT,
        target_type TEXT,
        source TEXT,
        confidence REAL,
        payload_json TEXT,
        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS overlay_best_practice (
        practice_id TEXT PRIMARY KEY,
        component_id TEXT,
        rule_id TEXT,
        severity TEXT,
        message TEXT
    );

    CREATE TABLE IF NOT EXISTS canon_variables (
        variable_id TEXT PRIMARY KEY,
        component_id TEXT,
        name TEXT,
        scope_level TEXT,
        access_type TEXT,
        lineno INTEGER,
        is_param INTEGER,
        type_hint TEXT
    );

    CREATE TABLE IF NOT EXISTS canon_scopes (
        scope_id TEXT PRIMARY KEY,
        component_id TEXT,
        parent_scope_id TEXT,
        scope_type TEXT,
        depth INTEGER
    );

    CREATE TABLE IF NOT EXISTS canon_types (
        type_id TEXT PRIMARY KEY,
        variable_id TEXT,
        component_id TEXT,
        type_annotation TEXT,
        inferred_type TEXT
    );

    CREATE TABLE IF NOT EXISTS call_graph_edges (
        edge_id TEXT PRIMARY KEY,
        caller_id TEXT,
        callee_id TEXT,
        call_kind TEXT,
        is_internal INTEGER,
        is_external INTEGER,
        is_builtin INTEGER,
        line_number INTEGER,
        resolved_name TEXT
    );

    CREATE TABLE IF NOT EXISTS rebuild_metadata (
        metadata_id TEXT PRIMARY KEY,
        component_id TEXT,
        indent_level INTEGER,
        has_docstring INTEGER,
        docstring_type TEXT,
        leading_comments TEXT,
        trailing_comments TEXT,
        formatting_hints TEXT
    );

    CREATE TABLE IF NOT EXISTS equivalence_proofs (
        proof_id TEXT PRIMARY KEY,
        file_id TEXT,
        original_ast_hash TEXT,
        rebuilt_ast_hash TEXT,
        ast_match INTEGER,
        semantic_equivalent INTEGER,
        proof_status TEXT,
        created_at TEXT
    );

    -- ===== PHASE 6: DRIFT DETECTION =====
    
    CREATE TABLE IF NOT EXISTS file_versions (
        version_id TEXT PRIMARY KEY,
        file_id TEXT,
        version_number INTEGER,
        previous_version_id TEXT,
        raw_hash TEXT,
        ast_hash TEXT,
        ingested_at TEXT,
        component_count INTEGER,
        change_summary TEXT
    );

    CREATE TABLE IF NOT EXISTS component_history (
        history_id TEXT PRIMARY KEY,
        component_id TEXT,
        qualified_name TEXT,
        file_version_id TEXT,
        previous_component_id TEXT,
        drift_type TEXT,
        source_hash TEXT,
        committed_hash TEXT,
        detected_at TEXT
    );

    CREATE TABLE IF NOT EXISTS drift_events (
        drift_id TEXT PRIMARY KEY,
        component_id TEXT,
        qualified_name TEXT,
        drift_category TEXT,
        severity TEXT,
        description TEXT,
        old_value TEXT,
        new_value TEXT,
        detected_at TEXT
    );
    """)

    conn.commit()
    return conn
