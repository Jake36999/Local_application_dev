
import math

class TelemetryNormalizer:
    def __init__(self):
        print("TelemetryNormalizer initialized.")

    def calculate_normalization_coefficients(self, k1_initial: float, k2_initial: float, delta_initial: float, Tf_initial: float) -> tuple[float, float]:
        """
        Calculates normalization coefficients for the state input signal vector X(t).
        For this simulation, it returns scaled versions of k1_initial and k2_initial.

        Args:
            k1_initial (float): Initial value for the k1 coefficient.
            k2_initial (float): Initial value for the k2 coefficient.
            delta_initial (float): Measured deviation (delta).
            Tf_initial (float): Phase-shifting constant.

        Returns:
            tuple[float, float]: A tuple containing the calculated (or scaled) k1 and k2 coefficients.
        """
        # In a real scenario, this would involve complex mathematical operations
        # to solve for k1 and k2 based on system dynamics and optimization goals.
        # For this subtask, as per instructions, we simulate this by applying a basic scaling.

        # Example: Let's assume a simple scaling or direct use for demonstration
        # A more complex implementation would involve solving equations like:
        # X(t) = [ k1 * delta \\ (k2 * s) / (Tf * s + 1) * delta ]

        calculated_k1 = k1_initial * (1 + delta_initial / 100) # Simple scaling example
        calculated_k2 = k2_initial * (1 - delta_initial / 200) # Simple scaling example

        print(f"  Initial k1: {k1_initial}, k2: {k2_initial}")
        print(f"  Measured deviation (delta): {delta_initial}")
        print(f"  Phase-shifting constant (Tf): {Tf_initial}")
        print(f"  Calculated k1: {calculated_k1}, k2: {calculated_k2}")

        return calculated_k1, calculated_k2

if __name__ == '__main__':
    normalizer = TelemetryNormalizer()

    # --- Test Case 1: Standard values ---
    print("\n--- Test Case 1: Standard values ---")
    k1, k2 = normalizer.calculate_normalization_coefficients(k1_initial=1.0, k2_initial=0.5, delta_initial=5.0, Tf_initial=0.1)
    assert isinstance(k1, float) and isinstance(k2, float), "Test 1 Failed: Coefficients should be floats."
    assert k1 == 1.0 * (1 + 5.0 / 100), "Test 1 Failed: k1 calculation mismatch."
    assert k2 == 0.5 * (1 - 5.0 / 200), "Test 1 Failed: k2 calculation mismatch."
    print("Test Case 1 Passed.")

    # --- Test Case 2: Zero deviation ---
    print("\n--- Test Case 2: Zero deviation ---")
    k1_zero, k2_zero = normalizer.calculate_normalization_coefficients(k1_initial=2.0, k2_initial=0.8, delta_initial=0.0, Tf_initial=0.05)
    assert k1_zero == 2.0, "Test 2 Failed: k1 should remain unchanged with zero delta."
    assert k2_zero == 0.8, "Test 2 Failed: k2 should remain unchanged with zero delta."
    print("Test Case 2 Passed.")

    # --- Test Case 3: Negative deviation (example of dynamic response) ---
    print("\n--- Test Case 3: Negative deviation ---")
    k1_neg, k2_neg = normalizer.calculate_normalization_coefficients(k1_initial=1.5, k2_initial=0.7, delta_initial=-10.0, Tf_initial=0.2)
    assert k1_neg == 1.5 * (1 - 10.0 / 100), "Test 3 Failed: k1 calculation mismatch for negative delta."
    assert k2_neg == 0.7 * (1 + 10.0 / 200), "Test 3 Failed: k2 calculation mismatch for negative delta."
    print("Test Case 3 Passed.")

    print("\nAll TelemetryNormalizer tests completed successfully!")
