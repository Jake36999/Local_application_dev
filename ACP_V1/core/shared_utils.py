"""
Shared utility functions for extraction and deployment logic used by both Packager and Orchestrator.
"""
import pathlib
import json
from typing import Any, Dict, List, Optional

def load_json_file(path: str) -> Any:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(path: str, data: Any) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def list_files_recursive(root: str, ignore_ext: Optional[List[str]] = None, ignore_dirs: Optional[List[str]] = None) -> List[str]:
    ignore_ext = ignore_ext or []
    ignore_dirs = set(ignore_dirs or [])
    result = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
        for filename in filenames:
            if any(filename.lower().endswith(ext) for ext in ignore_ext):
                continue
            result.append(str(pathlib.Path(dirpath) / filename))
    return result

def redact_sensitive_lines(content: str, keywords: Optional[List[str]] = None) -> str:
    keywords = keywords or ['api', 'key', 'secret', 'token', 'auth', 'password']
    lines = content.splitlines()
    redacted = []
    for line in lines:
        if any(k in line.lower() for k in keywords):
            redacted.append('[REDACTED]')
        else:
            redacted.append(line)
    return '\n'.join(redacted)
