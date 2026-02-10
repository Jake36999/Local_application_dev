import os
from pathlib import Path

# Target the config file
CONFIG_PATH = Path("config/settings.py")

# The correct configuration for LM Studio
NEW_SETTINGS = """
import os

# CENTRAL CONFIGURATION FOR ACP_V2
settings = {
    # --- AI BACKEND (LM Studio) ---
    # Ensure your LM Studio Local Server is running on Port 1234
    "EMBEDDING_API_URL": "http://localhost:1234/v1/embeddings",
    "LLM_API_URL": "http://localhost:1234/v1/chat/completions",
    "MODEL_NAME": "local-model",
    
    # --- SYSTEM PATHS ---
    "LOG_LEVEL": "INFO",
    "APP_NAME": "Aletheia ACP_v2",
    "STAGING_DIR": "staging",
}
"""

def apply_fix():
    print(f"🔧 Patching configuration at {CONFIG_PATH}...")
    
    # Ensure directory exists
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Overwrite with correct ports
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(NEW_SETTINGS.strip())
        
    print("✅ Configuration updated to Port 1234 (LM Studio Default).")
    print("👉 ACTION REQUIRED: Restart your Orchestrator terminal.")

if __name__ == "__main__":
    apply_fix()