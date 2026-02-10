import requests

# The "Plan" an LLM would generate
mock_llm_plan = {
    "workflow_name": "security_audit_test",
    "steps": [
        {
            "id": "step_1",
            "tool": "validate_path",
            "params": {"path": "./app"},
            "purpose": "Safety check"
        },
        {
            "id": "step_2",
            "tool": "profile_target",
            "params": {"path": "./app/main.py"},
            "purpose": "Check file stats"
        }
    ]
}

try:
    response = requests.post("http://127.0.0.1:8000/api/workflow", json=mock_llm_plan)
    print("Status Code:", response.status_code)
    print("Response:", response.json())
except Exception as e:
    print(f"Test failed: {e}")