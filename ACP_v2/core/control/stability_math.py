
import math

class StabilityAnalyzer:
    def __init__(self):
        print("StabilityAnalyzer initialized.")

    def analyze_stability(self, sigma: float, omega_p: float, ideal_omega_b_range: tuple = (0.5, 1.5)) -> dict:
        """
        Quantifies the damping factor (zeta) and verifies control bandwidth (omega_b).

        Args:
            sigma (float): The real part of the system eigenvalues (negative for stability).
            omega_p (float): The oscillation frequency (imaginary part of eigenvalues).
            ideal_omega_b_range (tuple): A tuple (min, max) representing the ideal control bandwidth range.

        Returns:
            dict: A dictionary containing the calculated damping factor, control bandwidth, and verification status.
        """
        if omega_p == 0 and sigma == 0:
            # Handle edge case for critically damped or undamped systems at origin
            zeta = 1.0 # Critically damped for stability
            control_bandwidth = 0.0
            bandwidth_maintained = False # Not actively controlling in this edge case
        elif sigma == 0:
            # Purely oscillatory (undamped), zeta is 0
            zeta = 0.0
            control_bandwidth = omega_p # Bandwidth is oscillation frequency
            bandwidth_maintained = (control_bandwidth >= ideal_omega_b_range[0] and control_bandwidth <= ideal_omega_b_range[1])
        elif omega_p == 0:
            # Overdamped or critically damped, no oscillation. zeta is 1.
            zeta = 1.0 # Or -1.0 if sigma is positive, but for stable systems, sigma < 0
            control_bandwidth = -sigma # Approximate for stable real poles
            bandwidth_maintained = (control_bandwidth >= ideal_omega_b_range[0] and control_bandwidth <= ideal_omega_b_range[1])
        else:
            # Calculate damping factor (zeta)
            # Ensure sigma is negative for a stable system (as per the problem statement's context of damping).
            # If sigma is positive, the system is unstable, and zeta calculation would still proceed
            # but would indicate instability.
            zeta = -sigma / math.sqrt(sigma**2 + omega_p**2)

            # Simulate control bandwidth (omega_b)
            # For demonstration, let's assume omega_b is proportional to omega_p for oscillatory systems
            # and related to sigma for non-oscillatory but stable systems.
            # This is a simplification; actual control bandwidth calculation is more complex.
            control_bandwidth = math.sqrt(sigma**2 + omega_p**2) # Magnitude of eigenvalue, often related to natural frequency

            # Verify if control bandwidth is maintained to prevent overshoot
            bandwidth_maintained = (control_bandwidth >= ideal_omega_b_range[0] and control_bandwidth <= ideal_omega_b_range[1])

        print(f"\nAnalyzing stability for sigma={sigma:.4f}, omega_p={omega_p:.4f}")
        print(f"  Calculated Damping Factor (zeta): {zeta:.4f}")
        print(f"  Simulated Control Bandwidth (omega_b): {control_bandwidth:.4f}")
        print(f"  Ideal Control Bandwidth Range: {ideal_omega_b_range}")
        print(f"  Control Bandwidth Maintained: {bandwidth_maintained}")

        return {
            'zeta': zeta,
            'control_bandwidth': control_bandwidth,
            'bandwidth_maintained': bandwidth_maintained
        }

if __name__ == '__main__':
    analyzer = StabilityAnalyzer()

    # Test Case 1: Underdamped stable system (sigma < 0, omega_p > 0)
    print("\n--- Test Case 1: Underdamped Stable System ---")
    results1 = analyzer.analyze_stability(sigma=-0.5, omega_p=1.0)
    assert math.isclose(results1['zeta'], 0.4472, rel_tol=1e-3), "Test 1 Failed: Zeta mismatch!"
    assert results1['bandwidth_maintained'] is True, "Test 1 Failed: Bandwidth not maintained!"
    print("Test Case 1 Passed.")

    # Test Case 2: Overdamped stable system (sigma < 0, omega_p = 0)
    print("\n--- Test Case 2: Overdamped Stable System ---")
    results2 = analyzer.analyze_stability(sigma=-1.0, omega_p=0.0)
    assert math.isclose(results2['zeta'], 1.0, rel_tol=1e-3), "Test 2 Failed: Zeta mismatch!"
    assert results2['bandwidth_maintained'] is True, "Test 2 Failed: Bandwidth not maintained!"
    print("Test Case 2 Passed.")

    # Test Case 3: Unstable system (sigma > 0)
    print("\n--- Test Case 3: Unstable System ---")
    results3 = analyzer.analyze_stability(sigma=0.2, omega_p=0.8)
    assert math.isclose(results3['zeta'], -0.2425, rel_tol=1e-3), "Test 3 Failed: Zeta mismatch!"
    assert results3['bandwidth_maintained'] is True, "Test 3 Failed: Bandwidth not maintained!"
    print("Test Case 3 Passed.")

    # Test Case 4: Critically damped (zeta = 1, typically sigma < 0, omega_p = 0, but can be approximated)
    # For real world critical damping, omega_p = 0 and sigma < 0 typically leads to zeta = 1
    print("\n--- Test Case 4: Critically Damped System (Simulated) ---")
    results4 = analyzer.analyze_stability(sigma=-0.8, omega_p=0.0)
    assert math.isclose(results4['zeta'], 1.0, rel_tol=1e-3), "Test 4 Failed: Zeta mismatch!"
    assert results4['bandwidth_maintained'] is True, "Test 4 Failed: Bandwidth not maintained!"
    print("Test Case 4 Passed.")

    # Test Case 5: Undamped (zeta = 0)
    print("\n--- Test Case 5: Undamped System ---")
    results5 = analyzer.analyze_stability(sigma=0.0, omega_p=1.5)
    assert math.isclose(results5['zeta'], 0.0, rel_tol=1e-3), "Test 5 Failed: Zeta mismatch!"
    assert results5['bandwidth_maintained'] is True, "Test 5 Failed: Bandwidth not maintained!"
    print("Test Case 5 Passed.")

    # Test Case 6: Bandwidth not maintained scenario
    print("\n--- Test Case 6: Bandwidth Not Maintained ---")
    results6 = analyzer.analyze_stability(sigma=-0.1, omega_p=0.05, ideal_omega_b_range=(1.0, 2.0))
    assert results6['bandwidth_maintained'] is False, "Test 6 Failed: Bandwidth should NOT be maintained!"
    print("Test Case 6 Passed.")

    print("\nAll StabilityAnalyzer tests completed successfully!")
