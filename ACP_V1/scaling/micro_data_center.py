
import uuid

class MicroDataCenterManager:
    def __init__(self):
        self.udcs = {}
        print("MicroDataCenterManager initialized.")

    def deploy_udc(self, udc_id: str, location: str, capacity: int) -> dict:
        """
        Simulates the deployment of a \u03bcDC.
        """
        if udc_id in self.udcs:
            print(f"Warning: \u03bcDC with ID {udc_id} already exists. Returning existing details.")
            return self.udcs[udc_id]

        udc_details = {
            'id': udc_id,
            'location': location,
            'capacity': capacity,
            'current_load': 0,
            'status': 'deployed'
        }
        self.udcs[udc_id] = udc_details
        print(f"\u03bcDC '{udc_id}' deployed at {location} with capacity {capacity}.")
        return udc_details

    def manage_udc_resource(self, udc_id: str, resource_request: int) -> bool:
        """
        Simulates managing resources within a deployed \u03bcDC.
        resource_request > 0: allocate resources.
        resource_request < 0: release resources.
        """
        if udc_id not in self.udcs:
            print(f"Error: \u03bcDC with ID {udc_id} not found.")
            return False

        udc = self.udcs[udc_id]
        new_load = udc['current_load'] + resource_request

        if resource_request > 0: # Allocation request
            if new_load <= udc['capacity']:
                udc['current_load'] = new_load
                print(f"Allocated {resource_request} units to \u03bcDC '{udc_id}'. New load: {udc['current_load']}/{udc['capacity']}.")
                return True
            else:
                print(f"Failed to allocate {resource_request} units to \u03bcDC '{udc_id}'. Insufficient capacity. Current load: {udc['current_load']}/{udc['capacity']}.")
                return False
        elif resource_request < 0: # Release request
            if new_load >= 0:
                udc['current_load'] = new_load
                print(f"Released {-resource_request} units from \u03bcDC '{udc_id}'. New load: {udc['current_load']}/{udc['capacity']}.")
                return True
            else:
                udc['current_load'] = 0 # Cannot go below zero load
                print(f"Released {-resource_request} units from \u03bcDC '{udc_id}'. Load cannot be negative, setting to 0.")
                return True
        else: # resource_request == 0
            print(f"No resource change requested for \u03bcDC '{udc_id}'.")
            return True

if __name__ == '__main__':
    print("--- Testing MicroDataCenterManager ---")
    manager = MicroDataCenterManager()

    # Test 1: Deploy a \u03bcDC
    print("\n--- Test Case 1: Deploy a \u03bcDC ---")
    udc1_details = manager.deploy_udc('udc-edge-001', 'FactoryFloor', 100)
    assert udc1_details['id'] == 'udc-edge-001', "Test 1 Failed: \u03bcDC ID mismatch!"
    assert udc1_details['status'] == 'deployed', "Test 1 Failed: \u03bcDC status mismatch!"
    assert manager.udcs['udc-edge-001'] == udc1_details, "Test 1 Failed: \u03bcDC not stored correctly!"
    print("Test Case 1 Passed.")

    # Test 2: Deploy an existing \u03bcDC (should return existing details)
    print("\n--- Test Case 2: Deploy existing \u03bcDC ---")
    udc1_details_again = manager.deploy_udc('udc-edge-001', 'Warehouse', 150) # Different location/capacity, but same ID
    assert udc1_details_again['location'] == 'FactoryFloor', "Test 2 Failed: Existing \u03bcDC details overwritten!"
    print("Test Case 2 Passed.")

    # Test 3: Allocate resources successfully
    print("\n--- Test Case 3: Allocate resources successfully ---")
    result_alloc1 = manager.manage_udc_resource('udc-edge-001', 30)
    assert result_alloc1 is True, "Test 3 Failed: Resource allocation should succeed!"
    assert manager.udcs['udc-edge-001']['current_load'] == 30, "Test 3 Failed: Load incorrect after allocation!"
    print("Test Case 3 Passed.")

    # Test 4: Allocate resources beyond capacity (should fail)
    print("\n--- Test Case 4: Allocate resources beyond capacity ---")
    result_alloc2 = manager.manage_udc_resource('udc-edge-001', 80) # 30 + 80 = 110 > 100
    assert result_alloc2 is False, "Test 4 Failed: Resource allocation beyond capacity should fail!"
    assert manager.udcs['udc-edge-001']['current_load'] == 30, "Test 4 Failed: Load should not change after failed allocation!"
    print("Test Case 4 Passed.")

    # Test 5: Release resources successfully
    print("\n--- Test Case 5: Release resources successfully ---")
    result_release1 = manager.manage_udc_resource('udc-edge-001', -15)
    assert result_release1 is True, "Test 5 Failed: Resource release should succeed!"
    assert manager.udcs['udc-edge-001']['current_load'] == 15, "Test 5 Failed: Load incorrect after release!"
    print("Test Case 5 Passed.")

    # Test 6: Attempt to manage resource for non-existent \u03bcDC
    print("\n--- Test Case 6: Manage non-existent \u03bcDC ---")
    result_non_existent = manager.manage_udc_resource('udc-edge-002', 10)
    assert result_non_existent is False, "Test 6 Failed: Managing non-existent \u03bcDC should fail!"
    print("Test Case 6 Passed.")

    # Test 7: Release more resources than currently loaded (load should go to 0)
    print("\n--- Test Case 7: Release excessive resources ---")
    result_release_excess = manager.manage_udc_resource('udc-edge-001', -20) # current_load is 15
    assert result_release_excess is True, "Test 7 Failed: Releasing excessive resources should succeed in setting load to 0!"
    assert manager.udcs['udc-edge-001']['current_load'] == 0, "Test 7 Failed: Load should be 0 after excessive release!"
    print("Test Case 7 Passed.")

    print("\nAll MicroDataCenterManager tests completed successfully!")
