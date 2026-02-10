
import collections

class ContractRegistry:
    def __init__(self):
        pass

    def validate_interaction(self, interaction_type: str, context_data: list) -> bool:
        """
        Validates service interactions based on predefined rules.

        Args:
            interaction_type (str): The type of interaction (
'IsFriend', 'IsFamily', 'IsStrange').
            context_data (list): A list of services or entities involved in the interaction.

        Returns:
            bool: True if the interaction is valid, False otherwise.
        """
        if interaction_type == 'IsFriend':
            # IsFriend: Allows concurrent execution, no specific checks for race conditions.
            return True
        elif interaction_type == 'IsFamily':
            # IsFamily: Requires sequential execution. If more than one service,
            # it implies potential concurrent access, making it invalid.
            # For simplicity, if there's only one service, it's considered safe (sequential by default).
            return len(context_data) <= 1
        elif interaction_type == 'IsStrange':
            # IsStrange: Enforces full isolation, meaning no direct interaction is allowed.
            return False
        else:
            print(f"Warning: Unknown interaction type '{interaction_type}'. Defaulting to invalid.")
            return False

if __name__ == '__main__':
    registry = ContractRegistry()

    print("\n--- Testing ContractRegistry --- ")

    # Test 1: IsFriend - valid (always True)
    print("\n--- Test Case 1: IsFriend with multiple services (expected: True) ---")
    assert (registry.validate_interaction('IsFriend', ['serviceA', 'serviceB']) is True), \
        "IsFriend failed: Should always be True"
    print("Test Case 1 Passed.")

    # Test 2: IsFamily - valid (single service, implies sequential)
    print("\n--- Test Case 2: IsFamily with single service (expected: True) ---")
    assert (registry.validate_interaction('IsFamily', ['serviceC']) is True), \
        "IsFamily failed: Should be True for single service"
    print("Test Case 2 Passed.")

    # Test 3: IsFamily - invalid (multiple services, implies concurrent risk)
    print("\n--- Test Case 3: IsFamily with multiple services (expected: False) ---")
    assert (registry.validate_interaction('IsFamily', ['serviceD', 'serviceE']) is False), \
        "IsFamily failed: Should be False for multiple services"
    print("Test Case 3 Passed.")

    # Test 4: IsStrange - invalid (always False)
    print("\n--- Test Case 4: IsStrange with any services (expected: False) ---")
    assert (registry.validate_interaction('IsStrange', ['serviceF']) is False), \
        "IsStrange failed: Should always be False"
    assert (registry.validate_interaction('IsStrange', []) is False), \
        "IsStrange failed: Should always be False even with no services"
    print("Test Case 4 Passed.")

    # Test 5: Unknown interaction type
    print("\n--- Test Case 5: Unknown interaction type (expected: False) ---")
    assert (registry.validate_interaction('UnknownType', ['serviceG']) is False), \
        "UnknownType failed: Should default to False"
    print("Test Case 5 Passed.")

    print("\nAll ContractRegistry tests completed successfully!")
