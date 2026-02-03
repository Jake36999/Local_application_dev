
import time
import random

class DRLGainTuner:
    def __init__(self, initial_kp=1.0, initial_ki=0.1, initial_kd=0.1):
        self.kp = initial_kp
        self.ki = initial_ki
        self.kd = initial_kd
        self.sampling_interval_ms = 20 # 20ms sampling interval
        print(f"DRLGainTuner initialized with initial gains: Kp={self.kp}, Ki={self.ki}, Kd={self.kd}")

    def _calculate_reward(self, error: float, change_in_error: float, output: float) -> float:
        """
        Simulates a reward function based on system state.
        Higher reward for smaller error, smaller change in error, and stable output.
        """
        stability_reward = -abs(error) * 10.0
        smoothness_reward = -abs(change_in_error) * 5.0
        output_magnitude_penalty = -abs(output) * 0.1 # Penalize large outputs to encourage efficiency

        # Add a slight reward for being close to optimal (e.g., error near zero)
        if abs(error) < 0.01: # Small error, good state
            stability_reward += 5.0

        total_reward = stability_reward + smoothness_reward + output_magnitude_penalty
        return total_reward

    def tune_gains(self, current_error: float, previous_error: float, current_output: float) -> tuple[float, float, float]:
        """
        Simulates real-time adjustment of controller gains (Kp, Ki, Kd)
        based on DRL-like optimization of a reward function.
        """
        dt = self.sampling_interval_ms / 1000.0 # Convert ms to seconds
        change_in_error = (current_error - previous_error) / dt

        reward = self._calculate_reward(current_error, change_in_error, current_output)

        # Simulate DRL-like exploration and exploitation for gain adjustment
        # For simplicity, we'll make small, random adjustments biased by reward
        learning_rate = 0.01
        exploration_factor = 0.05 # How much randomness to introduce

        # Adjust gains based on reward (simple gradient ascent simulation)
        # If reward is good, try to keep current direction or make smaller changes.
        # If reward is bad, explore more or reverse changes.

        # Simulate a policy that tries to improve gains based on reward
        # This is a highly simplified heuristic, not a true DQN training loop
        delta_kp = learning_rate * reward * (random.uniform(-1, 1) * exploration_factor + current_error)
        delta_ki = learning_rate * reward * (random.uniform(-1, 1) * exploration_factor + previous_error) # Using previous error as a proxy for integral effect
        delta_kd = learning_rate * reward * (random.uniform(-1, 1) * exploration_factor + change_in_error)

        # Apply adjustments, ensuring gains stay positive and within reasonable bounds
        self.kp = max(0.01, min(10.0, self.kp + delta_kp))
        self.ki = max(0.001, min(2.0, self.ki + delta_ki))
        self.kd = max(0.001, min(5.0, self.kd + delta_kd))

        return self.kp, self.ki, self.kd

if __name__ == '__main__':
    tuner = DRLGainTuner()

    print("\n--- Simulating DRL Gain Tuning Process ---")

    # Initial state
    current_error = 1.0
    previous_error = 1.2 # Simulating an initial state where error is decreasing
    current_output = 0.5

    print(f"\nInitial state: Error={current_error:.2f}, Prev Error={previous_error:.2f}, Output={current_output:.2f}")

    history = []
    num_steps = 10
    for i in range(num_steps):
        kp, ki, kd = tuner.tune_gains(current_error, previous_error, current_output)
        history.append({'step': i, 'kp': kp, 'ki': ki, 'kd': kd, 'error': current_error, 'output': current_output})

        print(f"Step {i+1}: Kp={kp:.4f}, Ki={ki:.4f}, Kd={kd:.4f}")

        # Simulate next state (simplified for testing)
        # Pretend the controller is working, reducing error over time
        previous_error = current_error
        current_error = max(0.0, current_error - random.uniform(0.05, 0.2))
        current_output = random.uniform(-0.1, 0.1) # Simulate controller output changing

        # Simple assertion: check if gains are within expected range
        assert 0.01 <= kp <= 10.0, f"Kp out of bounds: {kp}"
        assert 0.001 <= ki <= 2.0, f"Ki out of bounds: {ki}"
        assert 0.001 <= kd <= 5.0, f"Kd out of bounds: {kd}"

    print("\n--- DRL Gain Tuning Simulation Complete ---")
    print("Last recorded gains:")
    print(f"  Kp: {history[-1]['kp']:.4f}")
    print(f"  Ki: {history[-1]['ki']:.4f}")
    print(f"  Kd: {history[-1]['kd']:.4f}")
    print("All DRLGainTuner tests passed successfully (gains within bounds)!")
