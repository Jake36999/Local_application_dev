import hashlib
from pathlib import Path
from typing import Dict


def profile_target(path: str) -> Dict[str, object]:
    """Quickly profile a file: binary/text heuristic, size, and sha256 hash."""
    p = Path(path)
    if not p.exists():
        return {"error": "File not found"}

    is_binary = False
    try:
        with open(p, "rb") as handle:
            chunk = handle.read(1024)
            if b"\x00" in chunk:
                is_binary = True
    except Exception:
        is_binary = True

    file_hash = "N/A"
    if not is_binary:
        sha = hashlib.sha256()
        try:
            with open(p, "rb") as handle:
                while True:
                    piece = handle.read(4096)
                    if not piece:
                        break
                    sha.update(piece)
            file_hash = sha.hexdigest()
        except Exception:
            file_hash = "N/A"

    return {
        "filename": p.name,
        "extension": p.suffix,
        "size_bytes": p.stat().st_size,
        "is_binary": is_binary,
        "hash": file_hash,
    }
