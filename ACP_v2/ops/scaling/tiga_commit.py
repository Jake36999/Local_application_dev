
import time

class TigaCommit:
    def __init__(self, processing_overhead: float = 0.001):
        """
        Initializes the TigaCommit protocol simulator.
        Args:
            processing_overhead (float): A small constant for local processing time (epsilon).
        """
        self.processing_overhead = processing_overhead
        print(f"TigaCommit protocol simulator initialized with processing overhead (eps): {self.processing_overhead}s.")

    def commit_transaction(self, transaction_id: str, network_delay_estimate: float, participant_clocks: list) -> float:
        """
        Simulates the Tiga commit protocol using loosely synchronized clocks and
        network delay estimates to reduce geo-distributed transaction latency.

        Args:
            transaction_id (str): Unique identifier for the transaction.
            network_delay_estimate (float): Estimated network delay (Delta, in seconds).
            participant_clocks (list): A list of simulated clock values for participants.
                                      (For this simulation, their values are illustrative).

        Returns:
            float: The calculated end-to-end commit latency in seconds.
        """
        if network_delay_estimate < 0:
            raise ValueError("Network delay estimate cannot be negative.")

        # Simulate calculation of total commit latency: 2 * Delta + epsilon
        total_commit_latency = (2 * network_delay_estimate) + self.processing_overhead

        print(f"\n--- Tiga Commit Simulation for Transaction ID: {transaction_id} ---")
        print(f"  Network Delay Estimate (Δ): {network_delay_estimate:.4f}s")
        print(f"  Loosely Synchronized Participant Clocks (illustrative): {participant_clocks}")
        print(f"  Calculated Total Commit Latency (2*Δ + ε): {total_commit_latency:.4f}s")
        print(f"--- End Simulation for Transaction ID: {transaction_id} ---")

        return total_commit_latency

if __name__ == '__main__':
    tiga_protocol = TigaCommit()

    # --- Test Cases ---

    # Test 1: Standard network delay
    print("\n--- Test Case 1: Standard Network Delay (expected: ~0.051s) ---")
    transaction1_id = "TXN-001"
    delay1 = 0.025 # 25ms
    clocks1 = [1678886400.123, 1678886400.124]
    latency1 = tiga_protocol.commit_transaction(transaction1_id, delay1, clocks1)
    expected_latency1 = (2 * delay1) + tiga_protocol.processing_overhead
    assert isinstance(latency1, float), f"Test 1 Failed: Expected float latency, got {type(latency1)}"
    assert abs(latency1 - expected_latency1) < 1e-9, f"Test 1 Failed: Latency mismatch! Expected {expected_latency1:.4f}, got {latency1:.4f}"
    print("Test Case 1 Passed.")

    # Test 2: Higher network delay
    print("\n--- Test Case 2: Higher Network Delay (expected: ~0.201s) ---")
    transaction2_id = "TXN-002"
    delay2 = 0.100 # 100ms
    clocks2 = [1678886401.500, 1678886401.503]
    latency2 = tiga_protocol.commit_transaction(transaction2_id, delay2, clocks2)
    expected_latency2 = (2 * delay2) + tiga_protocol.processing_overhead
    assert isinstance(latency2, float), f"Test 2 Failed: Expected float latency, got {type(latency2)}"
    assert abs(latency2 - expected_latency2) < 1e-9, f"Test 2 Failed: Latency mismatch! Expected {expected_latency2:.4f}, got {latency2:.4f}"
    print("Test Case 2 Passed.")

    # Test 3: Zero network delay (edge case)
    print("\n--- Test Case 3: Zero Network Delay (expected: ~0.001s) ---")
    transaction3_id = "TXN-003"
    delay3 = 0.0
    clocks3 = [1678886402.000, 1678886402.000]
    latency3 = tiga_protocol.commit_transaction(transaction3_id, delay3, clocks3)
    expected_latency3 = (2 * delay3) + tiga_protocol.processing_overhead
    assert isinstance(latency3, float), f"Test 3 Failed: Expected float latency, got {type(latency3)}"
    assert abs(latency3 - expected_latency3) < 1e-9, f"Test 3 Failed: Latency mismatch! Expected {expected_latency3:.4f}, got {latency3:.4f}"
    print("Test Case 3 Passed.")

    # Test 4: Negative network delay (should raise ValueError)
    print("\n--- Test Case 4: Negative Network Delay (expected: ValueError) ---")
    transaction4_id = "TXN-004"
    delay4 = -0.01
    clocks4 = [1678886403.000]
    try:
        tiga_protocol.commit_transaction(transaction4_id, delay4, clocks4)
        assert False, "Test 4 Failed: ValueError was not raised for negative network delay!"
    except ValueError as e:
        print(f"  Caught expected error: {e}")
        assert "Network delay estimate cannot be negative." in str(e), "Test 4 Failed: Error message mismatch!"
    print("Test Case 4 Passed.")

    print("\nAll TigaCommit tests completed successfully!")
