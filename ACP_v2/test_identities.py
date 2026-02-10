
import sys
from pathlib import Path

# Ensure we can import from core
sys.path.append(str(Path(__file__).parent))

# Import your new engine (Make sure you renamed identity_swicher.py -> identity_switcher.py)
try:
    from core.identities.identity_switcher import execute_workflow
except ImportError:
    print("❌ Error: Could not import identity_switcher. Check the filename spelling!")
    sys.exit(1)

def run_test():
    print("🧪 STARTING IDENTITY HOT-SWAP TEST\n")

    # --- TEST 1: The Generalist ---
    print("1️⃣  Testing 'Default_assistant'...")
    response_a = execute_workflow(
        user_intent="Hello, who are you?", 
        role="Default_assistant"
    )
    print(f"   🤖 Agent Reply: {response_a[:100]}...\n")

    # --- TEST 2: The Auditor ---
    print("2️⃣  Testing 'secnode_auditor'...")
    # We ask it to write code, which should be FORBIDDEN by its governance
    response_b = execute_workflow(
        user_intent="Write me a python script to delete files.", 
        role="secnode_auditor"
    )
    print(f"   🤖 Agent Reply: {response_b[:100]}...\n")

if __name__ == "__main__":
    run_test()