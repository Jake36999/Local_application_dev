import collections
import time
from typing import List, Any

class IOLinker:
    def __init__(self):
        self.service_mesh_routes: List[Any] = []
        self.message_bus_contracts = collections.defaultdict(list)
        print("IOLinker initialized.")

    def update_routing_and_contracts(self, service_id: str, new_dependency_address: str, contract_details: dict) -> bool:
        """
        Simulates updating service-mesh routing and auto-populating the Message Bus
        with new IO contracts for immediate dependency re-linking.

        Args:
            service_id (str): The ID of the service whose routing is being updated.
            new_dependency_address (str): The new address of a dependency for the service.
            contract_details (dict): Details of the new IO contract to be published.

        Returns:
            bool: True if the update was simulated successfully, False otherwise.
        """
        print(f"\n--- Processing update for service '{service_id}' ---")

        # Simulate Service-Mesh Routing Update
        print(f"  Updating service-mesh route for '{service_id}' to point to dependency at '{new_dependency_address}'")
        self.service_mesh_routes.append({
            'service_id': service_id,
            'dependency': new_dependency_address,
            'last_updated': time.time()
        })

        # Simulate Message Bus Auto-Population with New IO Contracts
        print(f"  Auto-populating Message Bus with new IO contract for '{service_id}': {contract_details}")
        self.message_bus_contracts[service_id].append({
            'timestamp': time.time(),
            'contract': contract_details,
            'dependency_address': new_dependency_address
        })

        print(f"  Update for '{service_id}' simulated successfully.")
        return True

if __name__ == '__main__':
    linker = IOLinker()

    print("\n--- Test Case 1: Updating a new service's routing and contract ---")
    service_a = 'AuthService'
    dep_addr_a = 'http://auth-db-v2:8080'
    contract_a = {'type': 'database_connection', 'version': '2.0', 'security_level': 'high'}
    linker.update_routing_and_contracts(service_a, dep_addr_a, contract_a)

    # Verification for Test Case 1
    assert (linker.service_mesh_routes[-1]['dependency'] == dep_addr_a), \
        f"Test 1 Failed: Service-mesh route for {service_a} mismatch!"
    assert (len(linker.message_bus_contracts[service_a]) == 1), \
        f"Test 1 Failed: Message bus contracts for {service_a} count mismatch!"
    assert (linker.message_bus_contracts[service_a][0]['contract'] == contract_a), \
        f"Test 1 Failed: Message bus contract details for {service_a} mismatch!"
    print("Test Case 1 Passed: AuthService routing and contract updated.")

    print("\n--- Test Case 2: Updating an existing service with a new dependency ---")
    service_b = 'PaymentService'
    dep_addr_b_v1 = 'http://payment-gateway-v1:9000'
    contract_b_v1 = {'type': 'api_gateway', 'version': '1.0', 'latency_sla': '50ms'}
    linker.update_routing_and_contracts(service_b, dep_addr_b_v1, contract_b_v1)

    dep_addr_b_v2 = 'http://payment-gateway-v2:9001'
    contract_b_v2 = {'type': 'api_gateway', 'version': '2.0', 'latency_sla': '20ms'}
    linker.update_routing_and_contracts(service_b, dep_addr_b_v2, contract_b_v2)

    # Verification for Test Case 2
    assert (linker.service_mesh_routes[-1]['dependency'] == dep_addr_b_v2), \
        f"Test 2 Failed: Service-mesh route for {service_b} not updated to V2!"
    assert (len(linker.message_bus_contracts[service_b]) == 2), \
        f"Test 2 Failed: Message bus contracts for {service_b} count mismatch!"
    assert (linker.message_bus_contracts[service_b][1]['contract'] == contract_b_v2), \
        f"Test 2 Failed: Message bus contract V2 details for {service_b} mismatch!"
    print("Test Case 2 Passed: PaymentService updated with new dependency and contract.")

    print("\n--- All IOLinker tests completed successfully! ---")
