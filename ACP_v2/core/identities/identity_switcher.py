import json
import yaml
import re
import subprocess
import logging
from pathlib import Path
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam
from typing import List, Dict, Any, Optional
# Import AgentFactory and AgentIdentity
from .agent_factory import AgentFactory, AgentIdentity


# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ACP_Runtime")

# 1. Configuration
# In a real setup, these paths should be dynamic or env vars
ACP_ROOT = Path("ACP_v3_Master")
CLIENT = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

class GovernanceGuard:
    """Enforces pre-flight safety checks using Regex patterns."""
    def __init__(self, governance_config: Dict):
        self.prohibitions = governance_config.get("prohibitions", [])
        # Default safety net for SQL Injection / System commands if not specified
        self.patterns = [
            (r"(?i)\b(DROP|DELETE|TRUNCATE)\s+TABLE", "High-Risk SQL Detected"),
            (r"(?i)\b(rm\s+-rf|mkfs)", "Destructive System Command Detected"),
            (r"(?i)<script>", "XSS Pattern Detected")
        ]

    def check(self, user_input: str) -> bool:
        for pattern, reason in self.patterns:
            if re.search(pattern, user_input):
                logger.warning(f"🛡️ Governance Block: {reason}")
                return False
        return True

class IdentityManager:
    def __init__(self, role_name: str, identities_root: Path = ACP_ROOT / "identities"):
        """
        Args:
            role_name: The folder name of the identity (e.g., 'auditor')
            identities_root: Path to the identities directory
        """
        self.role_path = identities_root / role_name
        if not self.role_path.exists():
            raise ValueError(f"Identity path '{self.role_path}' not found.")
            
        # Use Factory to load the identity from this path
        self.factory = AgentFactory(str(self.role_path))
        self.identity = self.factory.load_identity()
        self.guard = GovernanceGuard(self.identity.governance_config)
        
    def get_system_prompt(self) -> str:
        return self.identity.system_prompt

    def get_memory_path(self) -> Path:
        """Determines which Vector DB partition to use based on role."""
        # Maps the role to the specific directory in 'memory/vectors/'
        # This assumes ACP_ROOT is the parent of 'memory'
        memory_root = ACP_ROOT / "memory" / "vectors"
        
        role_lower = self.identity.role.lower()
        
        if "auditor" in role_lower or "security" in role_lower:
            return memory_root / "codebase_index"
        elif "architect" in role_lower or "builder" in role_lower:
            # Architects might need canonical truth, or a specific infrastructure index
            return ACP_ROOT / "memory" / "canonical"
        else:
            return memory_root / "general_knowledge"
            
    def get_tools(self) -> List[Dict]:
        return self.identity.tools

def execute_workflow(user_intent: str, role: str = "default_assistant", identities_root: Path = ACP_ROOT / "identities"):
    """The Main Loop called by the UI."""
    
    # 1. Hot-Swap Identity
    try:
        manager = IdentityManager(role, identities_root)
    except Exception as e:
        return f"❌ Failed to load identity '{role}': {e}"
    
    # 2. Governance Pre-Flight
    if not manager.guard.check(user_intent):
        return "❌ Request blocked by Governance protocols."

    system_prompt = manager.get_system_prompt()
    memory_path = manager.get_memory_path()
    


    # 3. Configure LM Studio Request
    messages: List[ChatCompletionMessageParam] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_intent}
    ]



    # 4. Apply Specialist Constraints
    if "architect" in manager.identity.role.lower():
        messages.append({
            "role": "system",
            "content": "Output must match 'config_schema_v11.json'."
        })

    params = {
        "model": "local-model",
        "messages": messages,
        "temperature": 0.1 if "architect" in manager.identity.role.lower() else 0.7,
        "tools": manager.get_tools() or None
    }
    if "architect" in manager.identity.role.lower():
        params["response_format"] = {"type": "json_object"}

    # 5. Fire to Headless Server
    print(f"⚡ Switching to Identity: {role}")
    print(f"📂 Mounting Memory Partition: {memory_path}")

    try:
        completion = CLIENT.chat.completions.create(**params)  # type: ignore
        message = completion.choices[0].message

        # 6. Tool Execution Loop
        if getattr(message, "tool_calls", None):
            print(f"🛠️  Agent requested tools: {[t.function.name for t in message.tool_calls]}")
            messages.append(message) # Add the intent to call tools to history

            for tool in message.tool_calls:
                pipeline_dir = manager.role_path / "pipelines"
                if not pipeline_dir.exists():
                    pipeline_dir = manager.role_path / "40_pipelines"

                result_content = _execute_local_tool(tool, pipeline_dir)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool.id,
                    "content": result_content
                })

            # Follow-up with results
            print("🔄  Feeding tool results back to LLM...")
            final_response = CLIENT.chat.completions.create(
                model="local-model",
                messages=messages
            )
            return final_response.choices[0].message.content

        return message.content

    except Exception as e:
        logger.error(f"Runtime Error: {e}")
        return f"System Error: {str(e)}"

def _execute_local_tool(tool_call, pipeline_dir: Path) -> str:
    """Executes the actual Python script associated with the tool."""
    func_name = tool_call.function.name
    
    try:
        # Tool Name: run_runtime_smoke_test
        # Goal: Execute runtime_smoke_test.py
        
        script_stem = func_name.replace("run_", "")
        script_path = pipeline_dir / f"{script_stem}.py"
        
        if not script_path.exists():
            return f"Error: Executable script '{script_path.name}' not found in {pipeline_dir}. Ensure a corresponding .py file exists for the YAML pipeline."
            
        print(f"🚀 Executing: {script_path}")
        
        # Check if arguments were passed (optional, depending on script design)
        args_dict = json.loads(tool_call.function.arguments)
        cmd = ["python", str(script_path)]
        
        # If the script accepts arguments, pass them as a JSON string or flags
        # For this implementation, we pass the raw JSON args as a single argument
        if args_dict:
             cmd.append(json.dumps(args_dict))

        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            return f"Success:\n{result.stdout}"
        else:
            return f"Failure:\n{result.stderr}"

    except Exception as e:
        return f"Execution Exception: {str(e)}"