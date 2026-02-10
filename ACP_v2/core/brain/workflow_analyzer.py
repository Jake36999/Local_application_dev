
import collections

class WorkflowAnalyzer:
    def reset_graph(self):
        self.graph = collections.defaultdict(list)
        self.nodes = set()
        self.in_degree = collections.defaultdict(int)

    def __init__(self):
        self.graph = collections.defaultdict(list)
        self.nodes = set()
        self.in_degree = collections.defaultdict(int)

    def add_task(self, task_id, dependencies=None):
        self.nodes.add(task_id)
        if dependencies:
            for dep in dependencies:
                if dep not in self.nodes:
                    # Automatically add dependency if not already a node
                    self.nodes.add(dep)
                self.graph[dep].append(task_id)
                self.in_degree[task_id] += 1

    def build_dag(self, telemetry_data):
        """
        Builds a Directed Acyclic Graph (DAG) from telemetry data.
        Telemetry data is expected as a list of dictionaries, e.g.,
        [{'id': 'A', 'dependencies': [], 'duration': 10},
         {'id': 'B', 'dependencies': ['A'], 'duration': 5}]
        """
        self.reset_graph()  # Reset graph for new data

        # First pass: add all tasks as nodes and establish initial dependencies
        for task in telemetry_data:
            task_id = task['id']
            self.add_task(task_id, task.get('dependencies', []))

        # Perform topological sort to detect cycles
        sorted_nodes = []
        queue = collections.deque([node for node in self.nodes if self.in_degree[node] == 0])

        while queue:
            node = queue.popleft()
            sorted_nodes.append(node)

            for neighbor in self.graph[node]:
                self.in_degree[neighbor] -= 1
                if self.in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(sorted_nodes) != len(self.nodes):
            raise ValueError("Cycle detected in workflow dependencies. Cannot build a valid DAG.")

        return {
            'nodes': list(self.nodes),
            'edges': {node: neighbors for node, neighbors in self.graph.items() if neighbors},
            'topological_order': sorted_nodes
        }

    def get_dag_structure(self):
        return {
            'nodes': list(self.nodes),
            'edges': {node: neighbors for node, neighbors in self.graph.items() if neighbors}
        }

if __name__ == '__main__':
    analyzer = WorkflowAnalyzer()

    # --- Test Case 1: Valid DAG ---
    print("\n--- Test Case 1: Valid DAG ---")
    telemetry_data_valid = [
        {'id': 'A', 'dependencies': [], 'duration': 10},
        {'id': 'B', 'dependencies': ['A'], 'duration': 5},
        {'id': 'C', 'dependencies': ['A'], 'duration': 7},
        {'id': 'D', 'dependencies': ['B', 'C'], 'duration': 12}
    ]
    dag_valid = analyzer.build_dag(telemetry_data_valid)
    print("Generated DAG:", dag_valid)
    expected_nodes_valid = {'A', 'B', 'C', 'D'}
    assert set(dag_valid['nodes']) == expected_nodes_valid, "Valid DAG: Nodes mismatch!"
    assert 'A' in dag_valid['topological_order'] and dag_valid['topological_order'].index('A') < dag_valid['topological_order'].index('B'), "Valid DAG: Topological order A -> B failed!"
    assert 'A' in dag_valid['topological_order'] and dag_valid['topological_order'].index('A') < dag_valid['topological_order'].index('C'), "Valid DAG: Topological order A -> C failed!"
    assert dag_valid['topological_order'].index('B') < dag_valid['topological_order'].index('D') and \
           dag_valid['topological_order'].index('C') < dag_valid['topological_order'].index('D'), "Valid DAG: Topological order B,C -> D failed!"
    print("Test Case 1 passed: Valid DAG built successfully.")

    # --- Test Case 2: DAG with isolated task ---
    print("\n--- Test Case 2: DAG with isolated task ---")
    telemetry_data_isolated = [
        {'id': 'X', 'dependencies': [], 'duration': 1},
        {'id': 'Y', 'dependencies': [], 'duration': 2},
        {'id': 'Z', 'dependencies': ['X'], 'duration': 3}
    ]
    dag_isolated = analyzer.build_dag(telemetry_data_isolated)
    print("Generated DAG:", dag_isolated)
    expected_nodes_isolated = {'X', 'Y', 'Z'}
    assert set(dag_isolated['nodes']) == expected_nodes_isolated, "Isolated DAG: Nodes mismatch!"
    assert 'X' in dag_isolated['topological_order'] and dag_isolated['topological_order'].index('X') < dag_isolated['topological_order'].index('Z'), "Isolated DAG: Topological order X -> Z failed!"
    print("Test Case 2 passed: Isolated task handled successfully.")

    # --- Test Case 3: Cyclic Dependency (Expected to fail) ---
    print("\n--- Test Case 3: Cyclic Dependency (Expected to fail) ---")
    telemetry_data_cyclic = [
        {'id': 'P', 'dependencies': ['R'], 'duration': 1},
        {'id': 'Q', 'dependencies': ['P'], 'duration': 2},
        {'id': 'R', 'dependencies': ['Q'], 'duration': 3}
    ]
    try:
        analyzer.build_dag(telemetry_data_cyclic)
        assert False, "Cyclic DAG: Cycle was not detected!"
    except ValueError as e:
        print(f"Expected error caught: {e}")
        assert "Cycle detected" in str(e), "Cyclic DAG: Error message mismatch!"
    print("Test Case 3 passed: Cyclic dependency detected successfully.")

    # --- Test Case 4: Complex DAG with multiple paths ---
    print("\n--- Test Case 4: Complex DAG with multiple paths ---")
    telemetry_data_complex = [
        {'id': 'T1', 'dependencies': []},
        {'id': 'T2', 'dependencies': ['T1']},
        {'id': 'T3', 'dependencies': ['T1']},
        {'id': 'T4', 'dependencies': ['T2', 'T3']},
        {'id': 'T5', 'dependencies': ['T3']},
        {'id': 'T6', 'dependencies': ['T4', 'T5']}
    ]
    dag_complex = analyzer.build_dag(telemetry_data_complex)
    print("Generated DAG:", dag_complex)
    expected_nodes_complex = {'T1', 'T2', 'T3', 'T4', 'T5', 'T6'}
    assert set(dag_complex['nodes']) == expected_nodes_complex, "Complex DAG: Nodes mismatch!"
    assert dag_complex['topological_order'].index('T1') < dag_complex['topological_order'].index('T2'), "Complex DAG: T1->T2 failed!"
    assert dag_complex['topological_order'].index('T1') < dag_complex['topological_order'].index('T3'), "Complex DAG: T1->T3 failed!"
    assert dag_complex['topological_order'].index('T2') < dag_complex['topological_order'].index('T4') or \
           dag_complex['topological_order'].index('T3') < dag_complex['topological_order'].index('T4'), "Complex DAG: T2,T3->T4 failed!"
    assert dag_complex['topological_order'].index('T3') < dag_complex['topological_order'].index('T5'), "Complex DAG: T3->T5 failed!"
    assert dag_complex['topological_order'].index('T4') < dag_complex['topological_order'].index('T6') or \
           dag_complex['topological_order'].index('T5') < dag_complex['topological_order'].index('T6'), "Complex DAG: T4,T5->T6 failed!"
    print("Test Case 4 passed: Complex DAG built successfully.")

    print("\nAll WorkflowAnalyzer tests completed successfully!")
