import collections
import json
from typing import Dict, Any

class StackCreator:
    def __init__(self):
        pass

    def create_manifests(self, dag_data: Dict[str, Any]) -> list[dict]:
        """
        Translates a DAG-based plan into a list of simulated deployment manifests.
        For simplicity, each node in the DAG will correspond to a basic manifest.
        """
        if not isinstance(dag_data, dict) or 'nodes' not in dag_data:
            raise ValueError("Invalid DAG data format. Expected a dictionary with 'nodes' key.")

        manifests = []
        for node_id in dag_data['nodes']:
            # Simulate different manifest types based on node ID or other criteria
            if node_id.startswith('K8S_'):
                manifest_type = 'KubernetesDeployment'
                resource_name = node_id.lower().replace('k8s_', '')
                manifest = {
                    'apiVersion': 'apps/v1',
                    'kind': 'Deployment',
                    'metadata': {'name': resource_name},
                    'spec': {
                        'replicas': 1,
                        'selector': {'matchLabels': {'app': resource_name}},
                        'template': {
                            'metadata': {'labels': {'app': resource_name}},
                            'spec': {'containers': [{'name': resource_name, 'image': f'myregistry/{resource_name}:latest'}]}
                        }
                    }
                }
            elif node_id.startswith('FN_'):
                manifest_type = 'ServerlessFunction'
                resource_name = node_id.lower().replace('fn_', '')
                manifest = {
                    'service': resource_name,
                    'provider': {'name': 'aws', 'runtime': 'python3.9'},
                    'functions': {
                        resource_name: {
                            'handler': f'handler.main',
                            'events': [{'http': 'ANY /'}]
                        }
                    }
                }
            else:
                manifest_type = 'GenericTask'
                manifest = {
                    'task_id': node_id,
                    'description': f'Manifest for generic task {node_id}',
                    'dependencies': dag_data['edges'].get(node_id, [])
                }

            manifests.append({
                'type': manifest_type,
                'name': node_id,
                'manifest_content': manifest
            })

        return manifests

if __name__ == '__main__':
    creator = StackCreator()

    # --- Test Case 1: Simple DAG with mixed types ---+
    print("\n--- Test Case 1: Simple DAG with mixed types ---")
    sample_dag_1 = {
        'nodes': ['K8S_AuthService', 'FN_ProcessData', 'GenericTask_Log'],
        'edges': {
            'K8S_AuthService': ['FN_ProcessData'],
            'FN_ProcessData': ['GenericTask_Log']
        },
        'topological_order': ['K8S_AuthService', 'FN_ProcessData', 'GenericTask_Log']
    }
    manifests_1 = creator.create_manifests(sample_dag_1)
    print(f"Generated manifests (count: {len(manifests_1)}):\n")
    for m in manifests_1:
        print(json.dumps(m, indent=2))

    assert len(manifests_1) == 3, f"Expected 3 manifests, got {len(manifests_1)}"
    assert manifests_1[0]['name'] == 'K8S_AuthService'
    assert manifests_1[0]['type'] == 'KubernetesDeployment'
    assert 'apiVersion' in manifests_1[0]['manifest_content']

    assert manifests_1[1]['name'] == 'FN_ProcessData'
    assert manifests_1[1]['type'] == 'ServerlessFunction'
    assert 'provider' in manifests_1[1]['manifest_content']

    assert manifests_1[2]['name'] == 'GenericTask_Log'
    assert manifests_1[2]['type'] == 'GenericTask'
    assert 'task_id' in manifests_1[2]['manifest_content']
    print("Test Case 1 passed: Manifests generated and structure verified.")

    # --- Test Case 2: Empty DAG (Expected: empty list) ---
    print("\n--- Test Case 2: Empty DAG ---")
    sample_dag_2: Dict[str, Any] = {'nodes': [], 'edges': {}}
    manifests_2 = creator.create_manifests(sample_dag_2)
    print(f"Generated manifests (count: {len(manifests_2)}): {manifests_2}")
    assert len(manifests_2) == 0, f"Expected 0 manifests, got {len(manifests_2)}"
    print("Test Case 2 passed: Empty DAG handled correctly.")

    # --- Test Case 3: Invalid DAG format (Expected: ValueError) ---
    print("\n--- Test Case 3: Invalid DAG format ---")
    invalid_dag = "not a dict"
    try:
        creator.create_manifests(invalid_dag) # type: ignore[arg-type]
        assert False, "ValueError was not raised for invalid DAG format!"
    except ValueError as e:
        print(f"Expected error caught: {e}")
        assert "Invalid DAG data format" in str(e)
    print("Test Case 3 passed: Invalid DAG format handled.")

    print("\nAll StackCreator tests completed successfully!")
