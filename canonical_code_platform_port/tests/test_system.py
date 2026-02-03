import os
import sqlite3
import sys

import pytest

from core.ingest import main as ingest_main
from core.canon_db import init_db  # noqa: F401 ensures schema import side effects


def test_end_to_end_workflow(clean_db, sample_script):
    # 1) Ingest sample script
    sys.argv = ["ingest.py", sample_script]
    try:
        ingest_main()
    except SystemExit as e:
        assert e.code == 0

    assert os.path.exists("canon.db"), "canon.db should be created after ingestion"

    # 2) Verify database content
    conn = sqlite3.connect("canon.db")
    cursor = conn.cursor()

    files = cursor.execute("SELECT * FROM canon_files").fetchall()
    assert len(files) == 1

    comps = cursor.execute("SELECT * FROM canon_components").fetchall()
    assert len(comps) > 0

    # 3) Analysis tables exist (may be empty for tiny script)
    cursor.execute("SELECT * FROM canon_variables")

    conn.close()
