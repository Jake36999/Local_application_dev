from pydantic import BaseModel, ValidationError
from typing import List, Optional, Dict, Any

class Metadata(BaseModel):
    name: str
    version: Optional[str] = None
    author: Optional[str] = None

class Rule(BaseModel):
    condition: str
    action: str
    priority: int = 1

class AtomicLens(BaseModel):
    kind: str
    metadata: Metadata
    lens_type: str
    rules: List[Rule] = []

class DeploymentManifest(BaseModel):
    kind: str
    apiVersion: str = "v1"
    metadata: Metadata
    spec: Dict[str, Any]

SCHEMA_MAP = {
    "DeploymentManifest": DeploymentManifest,
    "AtomicLens": AtomicLens,
}

def validate_bundle_item(yaml_data: Dict[str, Any]) -> bool:
    kind = yaml_data.get("kind")
    if kind not in SCHEMA_MAP:
        return True
    model_class = SCHEMA_MAP[kind]
    try:
        model_class(**yaml_data)
        return True
    except ValidationError as e:
        print(f"❌ Schema Violation for '{yaml_data.get('metadata', {}).get('name', 'Unknown')}':")
        for error in e.errors():
            print(f"   - {error['loc']}: {error['msg']}")
        return False
