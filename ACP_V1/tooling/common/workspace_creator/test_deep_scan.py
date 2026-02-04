import requests
import json

# Simulating an LLM Workflow
llm_plan = {
    "workflow_name": "index_core_system",
    "steps": [
        # Step 1: Check if main.py is safe and readable
        {
            "id": "check_file",
            "tool": "profile_target",
            "params": {"path": "./app/main.py"},
            "purpose": "Verify file existence"
        },
        # Step 2: Extract Code Intelligence (Functions/Classes) to DB
        {
            "id": "index_logic",
            "tool": "canon_scan",
            "params": {"path": "./app/main.py"},
            "purpose": "Build knowledge graph"
        }
    ]
}

try:
    print("🚀 Sending Deep Scan Request...")
    response = requests.post("http://127.0.0.1:8000/api/workflow", json=llm_plan)
    
    if response.status_code == 200:
        print("\n✅ Workflow Successful!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"\n❌ Error {response.status_code}: {response.text}")

except Exception as e:
    print(f"Connection failed: {e}")