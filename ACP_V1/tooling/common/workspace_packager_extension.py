"""
Pydantic schema validation for workspace packager output.
"""
from pydantic import BaseModel, ValidationError
from typing import List, Dict, Any

class FileEntry(BaseModel):
    path: str
    size_bytes: int
    complexity: int
    summary: Dict[str, Any]
    content: str

class BundleMeta(BaseModel):
    project: str
    generated_at: str
    stats: Dict[str, Any]
    tree: str

class WorkspaceBundle(BaseModel):
    meta: BundleMeta
    files: List[FileEntry]

def validate_bundle(bundle: dict) -> bool:
    try:
        WorkspaceBundle(**bundle)
        return True
    except ValidationError as e:
        print(f"Validation error: {e}")
        return False
