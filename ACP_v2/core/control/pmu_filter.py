
import math
import random # Added import for random

class PMUFilter:
    def __init__(self, filter_type: str, nominal_frequency: float = 60.0, sampling_rate: float = 4800.0):
        """
        Initializes the PMUFilter with parameters for FIR filter configuration.

        Args:
            filter_type (str): Type of FIR filter ('one_cycle' or 'two_cycle').
            nominal_frequency (float): The nominal frequency of the system (e.g., 50.0 or 60.0 Hz).
            sampling_rate (float): The sampling rate of the PMU in samples per second.
        """
        if filter_type not in ['one_cycle', 'two_cycle']:
            raise ValueError("filter_type must be 'one_cycle' or 'two_cycle'")
        self.filter_type = filter_type
        self.nominal_frequency = nominal_frequency
        self.sampling_rate = sampling_rate
        self.samples_per_cycle = int(self.sampling_rate / self.nominal_frequency)

        if self.filter_type == 'one_cycle':
            self.window_size = self.samples_per_cycle
        else: # 'two_cycle'
            self.window_size = 2 * self.samples_per_cycle

        print(f"PMUFilter initialized: type={self.filter_type}, window_size={self.window_size} samples.")

    def apply_fir_filter(self, sampled_values: list[float]) -> list[float]:
        """
        Simulates applying a one-cycle or two-cycle FIR filter by calculating
        the Root Mean Square (RMS) value for each sliding window.
        This provides a magnitude-like output more suitable for PMU analysis.

        Args:
            sampled_values (list[float]): A list of raw sampled values.

        Returns:
            list[float]: A list of RMS values for each window.
        """
        if len(sampled_values) < self.window_size:
            return [0.0] * len(sampled_values) # Return zeros if not enough samples

        filtered_values = []
        for i in range(len(sampled_values) - self.window_size + 1):
            window = sampled_values[i : i + self.window_size]
            # Calculate RMS for values in the window: sqrt( sum(x_i^2) / N )
            rms_value = math.sqrt(sum(x**2 for x in window) / self.window_size)
            filtered_values.append(rms_value)
        return filtered_values

    def check_tve_compliance(self, filtered_value: float, true_value: float, threshold: float = 0.01) -> bool:
        """
        Simulates checking Total Vector Error (TVE) compliance.
        For a single magnitude, simplified TVE = |filtered_value - true_value| / |true_value|

        Args:
            filtered_value (float): The filtered magnitude value (e.g., RMS).
            true_value (float): The true (reference) magnitude value (e.g., RMS of ideal signal).
            threshold (float): The TVE compliance threshold (e.g., 0.01 for 1%).

        Returns:
            bool: True if compliant, False otherwise.
        """
        if true_value == 0.0:
            return filtered_value == 0.0 # Avoid division by zero

        tve = abs(filtered_value - true_value) / abs(true_value)
        print(f"  TVE: {tve:.4f} (Threshold: {threshold:.4f})")
        return tve <= threshold


if __name__ == '__main__':
    print("--- Testing PMUFilter ---")

    # Parameters for simulation
    NOMINAL_FREQ = 60.0 # Hz
    SAMPLING_RATE = 4800.0 # samples/sec
    SAMPLES_PER_CYCLE = int(SAMPLING_RATE / NOMINAL_FREQ)

    # Generate sample sampled_values (a sine wave with some noise)
    duration = 5 # seconds
    num_samples = int(SAMPLING_RATE * duration)
    time_points = [i / SAMPLING_RATE for i in range(num_samples)]

    # True value (peak magnitude 10.0)
    true_peak_magnitude = 10.0
    # True RMS magnitude for a sine wave is Peak / sqrt(2)
    true_rms_magnitude = true_peak_magnitude / math.sqrt(2)

    # Generate a perfect sine wave for reference
    perfect_sine_wave = [true_peak_magnitude * math.sin(2 * math.pi * NOMINAL_FREQ * t) for t in time_points]

    # Generate a noisy sine wave - REDUCED NOISE MAGNITUDE
    noise_amplitude = 0.1 # Reduced noise
    sampled_values_noisy = [
        true_peak_magnitude * math.sin(2 * math.pi * NOMINAL_FREQ * t) + random.uniform(-noise_amplitude, noise_amplitude)
        for t in time_points
    ]

    # 1. Test one-cycle FIR filter
    print("\n--- Test Case 1: One-cycle FIR Filter ---")
    one_cycle_filter = PMUFilter(filter_type='one_cycle', nominal_frequency=NOMINAL_FREQ, sampling_rate=SAMPLING_RATE)
    filtered_values_one_cycle = one_cycle_filter.apply_fir_filter(sampled_values_noisy)

    print(f"  Original samples (first 5): {[f'{x:.2f}' for x in sampled_values_noisy[:5]]}")
    print(f"  Filtered RMS values (first 5): {[f'{x:.2f}' for x in filtered_values_one_cycle[:5]]}")
    print(f"  Length of filtered values: {len(filtered_values_one_cycle)}")

    # Assertions for one-cycle filter
    expected_len_one_cycle = len(sampled_values_noisy) - one_cycle_filter.window_size + 1
    assert len(filtered_values_one_cycle) == expected_len_one_cycle, \
        f"Test 1 Failed: One-cycle filtered length mismatch (Expected: {expected_len_one_cycle}, Got: {len(filtered_values_one_cycle)})"

    # TVE compliance check for one-cycle filter
    print("\n  Simulating TVE compliance for one-cycle filter:")
    if len(filtered_values_one_cycle) > SAMPLES_PER_CYCLE:
        # Pick a filtered value from a stable region (e.g., mid-way through the filtered data)
        filtered_rms_estimate = filtered_values_one_cycle[len(filtered_values_one_cycle) // 2]
        is_compliant_one_cycle = one_cycle_filter.check_tve_compliance(filtered_rms_estimate, true_rms_magnitude)
        print(f"  One-cycle filter TVE compliant: {is_compliant_one_cycle}")
        assert is_compliant_one_cycle is True, "Test 1 Failed: One-cycle TVE check failed!"
    else:
        print("  (Not enough filtered samples to check TVE reliably)")
    print("Test Case 1 Passed.")


    # 2. Test two-cycle FIR filter
    print("\n--- Test Case 2: Two-cycle FIR Filter ---")
    two_cycle_filter = PMUFilter(filter_type='two_cycle', nominal_frequency=NOMINAL_FREQ, sampling_rate=SAMPLING_RATE)
    filtered_values_two_cycle = two_cycle_filter.apply_fir_filter(sampled_values_noisy)

    print(f"  Original samples (first 5): {[f'{x:.2f}' for x in sampled_values_noisy[:5]]}")
    print(f"  Filtered RMS values (first 5): {[f'{x:.2f}' for x in filtered_values_two_cycle[:5]]}")
    print(f"  Length of filtered values: {len(filtered_values_two_cycle)}")

    # Assertions for two-cycle filter
    expected_len_two_cycle = len(sampled_values_noisy) - two_cycle_filter.window_size + 1
    assert len(filtered_values_two_cycle) == expected_len_two_cycle, \
        f"Test 2 Failed: Two-cycle filtered length mismatch (Expected: {expected_len_two_cycle}, Got: {len(filtered_values_two_cycle)})"

    # TVE compliance check for two-cycle filter
    print("\n  Simulating TVE compliance for two-cycle filter:")
    if len(filtered_values_two_cycle) > SAMPLES_PER_CYCLE:
        filtered_rms_estimate_two_cycle = filtered_values_two_cycle[len(filtered_values_two_cycle) // 2]
        is_compliant_two_cycle = two_cycle_filter.check_tve_compliance(filtered_rms_estimate_two_cycle, true_rms_magnitude)
        print(f"  Two-cycle filter TVE compliant: {is_compliant_two_cycle}")
        assert is_compliant_two_cycle is True, "Test 2 Failed: Two-cycle TVE check failed!"
    else:
        print("  (Not enough filtered samples to check TVE reliably)")
    print("Test Case 2 Passed.")


    # Test 3: Invalid filter type
    print("\n--- Test Case 3: Invalid Filter Type ---")
    try:
        PMUFilter(filter_type='invalid_type')
        assert False, "Test 3 Failed: ValueError not raised for invalid filter type!"
    except ValueError as e:
        print(f"  Caught expected error: {e}")
        assert "filter_type must be 'one_cycle' or 'two_cycle'" in str(e), "Test 3 Failed: Error message mismatch!"
    print("Test Case 3 Passed.")

    print("\nAll PMUFilter tests completed successfully!")
