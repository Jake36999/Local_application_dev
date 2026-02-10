import hashlib
import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import PyPDF2

logger = logging.getLogger(__name__)

def generate_file_hash(file_path: Path) -> str:
    """Generates a SHA-256 hash of the file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        logger.error(f"Hash generation failed for {file_path}: {e}")
        return "error_hash"

def _parse_pdf_date(date_str: Optional[str]) -> Optional[str]:
    """Converts PDF-style date strings into ISO format."""
    if not date_str or not isinstance(date_str, str):
        return None
    
    clean_date = re.sub(r'[^0-9]', '', date_str)
    try:
        if len(clean_date) >= 8:
            return f"{clean_date[0:4]}-{clean_date[4:6]}-{clean_date[6:8]}"
    except Exception:
        pass
    return date_str

def _sanitize_string(text: Any) -> str:
    if not text or not isinstance(text, str):
        return "Unknown"
    clean_text = "".join(char for char in text if char.isprintable())
    return " ".join(clean_text.split())

def extract_document_metadata(reader: PyPDF2.PdfReader, file_path: Path, content: str = "") -> Dict[str, Any]:
    """Generates an enriched document profile."""
    try:
        meta = reader.metadata
    except Exception:
        meta = None

    word_count = len(content.split()) if content else 0

    return {
        "file_hash": generate_file_hash(file_path),
        "file_name": file_path.name,
        "internal_title": _sanitize_string(meta.title if meta and meta.title else file_path.stem),
        "author": _sanitize_string(meta.author if meta and meta.author else "Unknown Author"),
        "total_pages": len(reader.pages),
        "word_count": word_count,
        "creation_date": _parse_pdf_date(meta.get('/CreationDate') if meta else None),
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "version": "2.2"
    }