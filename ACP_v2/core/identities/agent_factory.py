import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AgentFactory")

@dataclass
class AgentIdentity:
    name: str
    role: str
    system_prompt: str
    tools: List[Dict[str, Any]]
    schemas: Dict[str, Any]
    governance_config: Dict[str, Any]

class AgentFactory:
    def __init__(self, onboarding_path: str):
        self.base_path = Path(onboarding_path)
        if not self.base_path.exists():
            raise FileNotFoundError(f"Onboarding folder not found at {onboarding_path}")

    def load_identity(self) -> AgentIdentity:
        """Orchestrates the loading of all agent components."""
        manifest = self._load_manifest()
        governance = self._load_governance()
        
        system_prompt = self._construct_system_prompt(manifest, governance)
        tools = self._load_pipelines_as_tools()
        schemas = self._load_schemas()

        return AgentIdentity(
            name=manifest.get("agent_name", "Unknown Agent"),
            role=manifest.get("role", "Assistant"),
            system_prompt=system_prompt,
            tools=tools,
            schemas=schemas,
            governance_config=governance
        )

    def _load_manifest(self) -> Dict[str, Any]:
        """Reads 10_agent_manifest.json"""
        path = self.base_path / "10_agent_manifest.json"
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_governance(self) -> Dict[str, Any]:
        """Reads 20_governance_contracts.yaml"""
        path = self.base_path / "20_governance_contracts.yaml"
        if not path.exists():
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _construct_system_prompt(self, manifest: Dict, governance: Dict) -> str:
        """Combines manifest, prompt file, and governance into one system message."""
        
        # 1. Base Identity
        prompt_parts = [
            f"IDENTITY: You are {manifest.get('agent_name')}, a {manifest.get('role')}.",
            f"VERSION: {manifest.get('version')}",
            f"CAPABILITIES: {', '.join(manifest.get('capabilities', []))}",
            "\n--- PRIME DIRECTIVE ---"
        ]

        # 2. Inject 00_START_HERE_PROMPT.md
        prompt_path = self.base_path / "00_START_HERE_PROMPT.md"
        if prompt_path.exists():
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_parts.append(f.read())

        # 3. Inject Governance (Thou Shalt Nots)
        if "prohibitions" in governance:
            prompt_parts.append("\n--- GOVERNANCE CONTRACTS (STRICT) ---")
            for rule in governance["prohibitions"]:
                prompt_parts.append(f"- {rule}")

        full_prompt = "\n".join(prompt_parts)
        
        # --- TOKEN SAFETY CHECK (Heuristic: 4 chars ~= 1 token) ---
        est_tokens = len(full_prompt) / 4
        if est_tokens > 2000:
            logger.warning(f"⚠️  High Context Load: System prompt is ~{int(est_tokens)} tokens. This may reduce reasoning capacity.")
            
        return full_prompt

    def _load_pipelines_as_tools(self) -> List[Dict[str, Any]]:
        """Converts YAML pipelines in 40_pipelines to OpenAI Tool definitions."""
        tools = []
        pipeline_dir = self.base_path / "40_pipelines"
        
        if not pipeline_dir.exists():
            return []

        for file in pipeline_dir.glob("*.yaml"):
            # Simple heuristic: Create a tool that can trigger this pipeline
            tool_name = f"run_{file.stem}" 
            description = f"Executes the workflow defined in {file.name}"
            
            # In a real scenario, you'd parse the YAML to find actual input parameters.
            # Here we create a generic trigger tool.
            tool_def = {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": description,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "rationale": {
                                "type": "string",
                                "description": "Why this workflow is being triggered."
                            }
                        },
                        "required": ["rationale"]
                    }
                }
            }
            tools.append(tool_def)
            
        return tools

    def _load_schemas(self) -> Dict[str, Any]:
        """Loads JSON schemas from 30_schemas for Structured Output."""
        schemas = {}
        schema_dir = self.base_path / "30_schemas"
        
        if not schema_dir.exists():
            return {}

        for file in schema_dir.glob("*.json"):
            with open(file, 'r', encoding='utf-8') as f:
                schemas[file.stem] = json.load(f)
        
        return schemas