# Test file for Phase 6: Drift Detection
# VERSION 2 - Modified implementation with drift

import math  # NEW IMPORT (drift: import_change)

def calculate(x, y, operation="add"):  # MODIFIED SIGNATURE (drift: signature_change)
    """Enhanced calculator with multiple operations."""
    if operation == "add":
        return x + y
    elif operation == "multiply":
        return x * y  # NEW BEHAVIOR (drift: call_graph_change)
    else:
        return x - y

def process_data(data):
    """Process incoming data with validation."""
    results = []
    validated_count = 0  # NEW VARIABLE (drift: symbol_change)
    for item in data:
        if isinstance(item, (int, float)):  # NEW LOGIC
            results.append(item * 2)
            validated_count += 1  # NEW VARIABLE USAGE
    print(f"Validated {validated_count} items")  # NEW CALL (drift: call_graph_change)
    return results

# REMOVED: class DataProcessor (drift: REMOVED component)

def new_helper():  # NEW FUNCTION (drift: ADDED component)
    """Newly added helper function."""
    return math.sqrt(42)  # Uses new import
