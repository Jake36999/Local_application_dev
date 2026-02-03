
import collections
import random

class AdaptiveProtectionSystem:
    def __init__(self, default_relay_setting: float = 1.0, default_isolation_parameter: int = 100):
        """
        Initializes the AdaptiveProtectionSystem with default settings.

        Args:
            default_relay_setting (float): The default value for relay settings (e.g., trip current).
            default_isolation_parameter (int): The default value for fault isolation (e.g., segment size).
        """
        self.default_relay_setting = default_relay_setting
        self.default_isolation_parameter = default_isolation_parameter
        self.current_relay_setting = default_relay_setting
        self.current_isolation_parameter = default_isolation_parameter
        print(f"AdaptiveProtectionSystem initialized with default relay setting: {default_relay_setting}, isolation parameter: {default_isolation_parameter}.")

    def adjust_protection_settings(self, network_condition: str, topology_change: dict):
        """
        Dynamically adjusts relay settings and fault isolation parameters
        based on real-time network conditions and topology changes.

        Args:
            network_condition (str): Current network condition ('stable', 'congested', 'faulty').
            topology_change (dict): Dictionary describing topology changes, e.g.,
                                   {'node_down': 'node-1'}, {'link_up': 'link-5'}, or {}.
        """
        print(f"\nAdjusting protection settings for network condition: '{network_condition}', topology change: {topology_change}")

        initial_relay = self.current_relay_setting
        initial_isolation = self.current_isolation_parameter

        if network_condition == 'faulty':
            # Aggressive settings for faulty conditions
            self.current_relay_setting = self.default_relay_setting * 0.8 # Lower trip current
            self.current_isolation_parameter = max(50, self.default_isolation_parameter // 2) # Smaller isolation segments
            print(f"  Network is faulty. Adjusted to more aggressive settings. Relay: {self.current_relay_setting:.2f}, Isolation: {self.current_isolation_parameter}")
        elif network_condition == 'congested':
            # Slightly less aggressive, prioritize stability
            self.current_relay_setting = self.default_relay_setting * 0.9
            self.current_isolation_parameter = self.default_isolation_parameter // 1 # No change, but could be adjusted
            print(f"  Network is congested. Adjusted to balanced settings. Relay: {self.current_relay_setting:.2f}, Isolation: {self.current_isolation_parameter}")
        elif network_condition == 'stable':
            # Relaxed settings for stable conditions
            self.current_relay_setting = self.default_relay_setting * 1.1 # Higher trip current (less sensitive)
            self.current_isolation_parameter = self.default_isolation_parameter * 1 # No change, could be wider segments
            print(f"  Network is stable. Adjusted to relaxed settings. Relay: {self.current_relay_setting:.2f}, Isolation: {self.current_isolation_parameter}")
        else:
            print(f"  Unknown network condition '{network_condition}'. Maintaining current settings.")

        # React to topology changes
        if 'node_down' in topology_change:
            print(f"  Topology change: Node '{topology_change['node_down']}' is down. Increasing isolation granularity.")
            self.current_isolation_parameter = max(30, self.current_isolation_parameter // 2)
        elif 'link_up' in topology_change:
            print(f"  Topology change: Link '{topology_change['link_up']}' is up. Potentially relaxing isolation slightly.")
            self.current_isolation_parameter = min(self.default_isolation_parameter, self.current_isolation_parameter + 10)

        if self.current_relay_setting != initial_relay or self.current_isolation_parameter != initial_isolation:
            print(f"  Settings changed: Relay from {initial_relay:.2f} to {self.current_relay_setting:.2f}, Isolation from {initial_isolation} to {self.current_isolation_parameter}.")
        else:
            print("  No changes to settings applied.")


if __name__ == '__main__':
    print("--- Testing AdaptiveProtectionSystem ---")
    system = AdaptiveProtectionSystem(default_relay_setting=10.0, default_isolation_parameter=200)

    # Scenario 1: Faulty network, no topology change
    print("\n--- Test Case 1: Faulty Network ---")
    system.adjust_protection_settings('faulty', {})
    assert system.current_relay_setting == 10.0 * 0.8, "Test 1 Failed: Relay setting not adjusted for faulty network."
    assert system.current_isolation_parameter == 200 // 2, "Test 1 Failed: Isolation not adjusted for faulty network."
    print("Test Case 1 Passed.")

    # Scenario 2: Congested network, no topology change
    print("\n--- Test Case 2: Congested Network ---")
    system.adjust_protection_settings('congested', {})
    assert system.current_relay_setting == 10.0 * 0.9, "Test 2 Failed: Relay setting not adjusted for congested network."
    assert system.current_isolation_parameter == 200, "Test 2 Failed: Isolation should remain at 200." # Corrected assertion
    print("Test Case 2 Passed.")

    # Scenario 3: Stable network, node going down
    print("\n--- Test Case 3: Stable Network, Node Down ---")
    # Reset to default for a fresh scenario or continue from previous state
    system = AdaptiveProtectionSystem(default_relay_setting=10.0, default_isolation_parameter=200)
    system.adjust_protection_settings('stable', {'node_down': 'node-1'})
    assert system.current_relay_setting == 10.0 * 1.1, "Test 3 Failed: Relay setting not adjusted for stable network."
    assert system.current_isolation_parameter == max(30, 200 // 2), "Test 3 Failed: Isolation not adjusted for node down."
    print("Test Case 3 Passed.")

    # Scenario 4: Faulty network, link coming up
    print("\n--- Test Case 4: Faulty Network, Link Up ---")
    system = AdaptiveProtectionSystem(default_relay_setting=10.0, default_isolation_parameter=200)
    system.adjust_protection_settings('faulty', {'link_up': 'link-5'})
    assert system.current_relay_setting == 10.0 * 0.8, "Test 4 Failed: Relay setting not adjusted for faulty network."
    # Isolation should be 100 from faulty, then 100+10 = 110 (capped by default of 200)
    assert system.current_isolation_parameter == min(system.default_isolation_parameter, (system.default_isolation_parameter // 2) + 10), "Test 4 Failed: Isolation not adjusted for link up in faulty network."
    print("Test Case 4 Passed.")

    # Scenario 5: Unknown network condition
    print("\n--- Test Case 5: Unknown Network Condition ---")
    system = AdaptiveProtectionSystem(default_relay_setting=10.0, default_isolation_parameter=200)
    system.adjust_protection_settings('unknown', {})
    assert system.current_relay_setting == 10.0, "Test 5 Failed: Relay setting should remain default for unknown condition."
    assert system.current_isolation_parameter == 200, "Test 5 Failed: Isolation should remain default for unknown condition."
    print("Test Case 5 Passed.")

    print("\nAll AdaptiveProtectionSystem tests completed successfully!")
