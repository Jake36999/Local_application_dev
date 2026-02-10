import os
import sys
from pathlib import Path

import pytest

# Add project root to sys.path so imports resolve
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def clean_db():
    """Remove canon.db before/after each test."""
    db_path = Path("canon.db")
    if db_path.exists():
        db_path.unlink()
    yield
    # Optional cleanup after tests
    # if db_path.exists():
    #     db_path.unlink()


@pytest.fixture
def sample_script():
    """Create a temporary Python file for ingestion tests."""
    content = """
import os
def test_func():
    print("Hello World")
class TestClass:
    pass
"""
    filename = Path("temp_test_ingest.py")
    filename.write_text(content)
    yield str(filename)
    if filename.exists():
        filename.unlink()
