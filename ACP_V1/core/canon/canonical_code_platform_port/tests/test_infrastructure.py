import os
import sqlite3
import pytest
from pathlib import Path

# Core system entry points that must exist
REQUIRED_FILES = [
    'orchestrator.py',
    'ui_app.py',
    'bus/message_bus.py',
    'core/canon_db.py',
    'orchestrator_config.json'
]

# Databases that should be initialized
REQUIRED_DBS = [
    'canon.db',
    'orchestrator_bus.db',
    'settings.db'
]

def test_core_files_exist():
    """Verify critical system files are present."""
    missing = [f for f in REQUIRED_FILES if not os.path.exists(f)]
    assert not missing, f"Missing core files: {missing}"

def test_databases_exist():
    """Verify databases are initialized."""
    missing = [db for db in REQUIRED_DBS if not os.path.exists(db)]
    assert not missing, f"Missing databases: {missing}"

def test_staging_structure():
    """Verify staging directory structure."""
    staging = Path('staging')
    assert staging.exists(), "Staging directory missing"
    
    subdirs = ['incoming', 'processed', 'failed', 'archive']
    for sub in subdirs:
        assert (staging / sub).exists(), f"Missing staging subdir: {sub}"

def test_db_connections():
    """Verify database connectivity."""
    for db_name in REQUIRED_DBS:
        if os.path.exists(db_name):
            try:
                conn = sqlite3.connect(db_name)
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                conn.close()
            except sqlite3.Error as e:
                pytest.fail(f"Could not connect to {db_name}: {e}")