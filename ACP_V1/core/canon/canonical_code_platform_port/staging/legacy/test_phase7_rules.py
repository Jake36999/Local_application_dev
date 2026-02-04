# Test file for Phase 7: Governance Rules

# @extract|@pure
def compute_sum(numbers):
    """Pure compute function - no IO, no globals."""
    total = 0
    for n in numbers:
        total += n
    return total

# @extract
def calculate_average(numbers):
    """Compute average - eligible for extraction."""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

# @pure (but has IO - violation!)
def validate_and_save(data):
    """THIS VIOLATES P7-G1: marked @pure but has IO."""
    if not data:
        return False
    # This IO call violates the @pure directive
    print(f"Saving data: {data}")
    return True

# @io_boundary
def read_config():
    """IO boundary - allowed to perform IO."""
    with open("config.txt", "r") as f:
        return f.read()

# This should have coupling warning
# @extract
def orchestrator_function():
    """Has many dependencies - violates P7-G3."""
    compute_sum([1, 2, 3])
    calculate_average([1, 2, 3])
    validate_and_save({"key": "value"})
    read_config()
    compute_sum([4, 5, 6])
    calculate_average([7, 8, 9])
    return "done"

# Global state - violation!
global_counter = 0

# @pure (but modifies global - violation!)
def increment_counter():
    """VIOLATES P7-G2: marked @pure but accesses global."""
    global global_counter
    global_counter += 1
    return global_counter
