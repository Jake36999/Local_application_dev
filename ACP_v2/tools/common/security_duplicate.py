from pathlib import Path
from typing import Optional


_FORBIDDEN = [Path("C:/Windows"), Path("/etc"), Path("/sys"), Path("/proc")]


def _is_forbidden(path_obj: Path) -> bool:
    for forbidden in _FORBIDDEN:
        try:
            path_obj.resolve().relative_to(forbidden)
            return True
        except ValueError:
            continue
    return False


def validate_path(path: str, must_exist: bool = True) -> bool:
    """Validate a path for traversal and forbidden roots."""
    try:
        candidate = Path(path).resolve()
        if ".." in str(candidate):
            return False
        if _is_forbidden(candidate):
            return False
        if must_exist and not candidate.exists():
            return False
        return True
    except Exception:
        return False


def sanitize_path(path: str) -> Optional[Path]:
    """Return a safe Path or None if invalid."""
    return Path(path).resolve() if validate_path(path) else None
