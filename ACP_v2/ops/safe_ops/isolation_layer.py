
import re
import time
import uuid
from typing import Any

# Define custom exceptions here to ensure they are available within the subprocess execution
class MemoryAccessError(Exception):
    """Custom exception for unauthorized memory access."""
    pass

class HeapIsolationError(Exception):
    """Custom exception for heap isolation violations (temporal or type errors)."""
    pass

class MemoryIsolator:
    def __init__(self):
        pass

    def isolate_code_execution(self, code_to_execute: str, safe_memory_objects: list[str]) -> str:
        """
        Simulates symbolic execution to identify and prevent agent-generated code
        from accessing memory objects not explicitly declared as safe.
        """
        accessed_identifiers = set(re.findall(r'\\b[a-zA-Z_][a-zA-Z0-9_]*\\b', code_to_execute))

        python_builtins_keywords = {
            'print', 'if', 'else', 'for', 'in', 'while', 'def', 'class', 'return',
            'import', 'from', 'as', 'try', 'except', 'finally', 'with', 'open', 'len',
            'range', 'True', 'False', 'None', 'and', 'or', 'not', 'is', 'pass', 'break', 'continue',
            'uuid', 'time', # Added for the HeapIsolator example
        }
        accessed_identifiers = accessed_identifiers - python_builtins_keywords

        for identifier in accessed_identifiers:
            if identifier not in safe_memory_objects:
                raise MemoryAccessError(
                    "Unauthorized access detected: Code attempts to use '{}' which is not in the list of safe memory objects.".format(identifier)
                )

        return f"Symbolic execution successful. No unsafe memory access detected for code: '{code_to_execute[:50]}...'"

class HeapIsolator:
    def __init__(self):
        # Simulate heap as a dictionary of isolated regions
        # Each region stores objects, identified by a unique key (object_id)
        # Object structure: {'value': actual_value, 'type': object_type, 'allocated_time': time, 'freed': False}
        self.isolated_regions: dict[str, dict[str, dict[str, Any]]] = {
            'sensitive_data': {},
            'temporary_data': {},
            'long_lived_data': {}
        }
        print("HeapIsolator initialized with isolated regions.")

    def _get_object_region(self, obj_type: str) -> dict:
        """Helper to get the correct isolated region for an object type."""
        if obj_type not in self.isolated_regions:
            raise HeapIsolationError(f"Unknown object type '{obj_type}'. No dedicated heap region.")
        return self.isolated_regions[obj_type]

    def allocate_object_to_heap(self, object_id: str, obj_type: str, value: Any):
        """
        Allocates an object to its designated isolated heap region.
        Each object gets a unique ID to simulate its memory address.
        """
        region = self._get_object_region(obj_type)
        if object_id in region:
            raise HeapIsolationError(f"Object ID '{object_id}' already exists in heap.")

        region[object_id] = {
            'value': value,
            'type': obj_type,
            'allocated_time': time.time(),
            'freed': False
        }
        # print(f"  Allocated '{object_id}' (type: {obj_type}) to heap.")

    def retrieve_object_from_heap(self, object_id: str, expected_obj_type: str) -> Any:
        """
        Retrieves an object from the heap, ensuring type and temporal safety.
        Raises HeapIsolationError if type mismatch or temporal error (freed object).
        """
        for region_name, region in self.isolated_regions.items():
            if object_id in region:
                obj = region[object_id]
                if obj['freed']:
                    raise HeapIsolationError(f"Temporal Error: Object '{object_id}' (type: {obj['type']}) has been freed.")
                if obj['type'] != expected_obj_type:
                    raise HeapIsolationError(f"Type Error: Object '{object_id}' is of type '{obj['type']}', but '{expected_obj_type}' was expected.")
                # print(f"  Retrieved '{object_id}' (type: {obj['type']}).")
                return obj['value']
        raise HeapIsolationError(f"Object ID '{object_id}' not found in any heap region.")

    def free_object_from_heap(self, object_id: str):
        """
        Simulates freeing an object from the heap. The object remains, but is marked as freed
        to prevent temporal errors upon access.
        """
        for region_name, region in self.isolated_regions.items():
            if object_id in region:
                obj = region[object_id]
                obj['freed'] = True
                # print(f"  Freed '{object_id}' (type: {obj['type']}).")
                return
        raise HeapIsolationError(f"Object ID '{object_id}' not found to be freed.")


if __name__ == '__main__':
    isolator = MemoryIsolator()
    heap_isolator = HeapIsolator()

    # --- MemoryIsolator Test Cases (from previous iteration, ensuring they still work) ---
    # --- Test Case 1: Safe execution ---
    print("\n--- MemoryIsolator Test Case 1: Safe execution ---")
    safe_memory_context = ['data', 'process_record', 'result']
    safe_code = "result = process_record(data)"
    try:
        response = isolator.isolate_code_execution(safe_code, safe_memory_context)
        print(response)
        assert "No unsafe memory access detected" in response, "Test 1 Failed: Expected safe execution."
        print("MemoryIsolator Test Case 1 Passed.")
    except MemoryAccessError as e:
        print(f"MemoryIsolator Test 1 Failed: Unexpected MemoryAccessError: {e}")

    # --- Test Case 2: Attempt to access unsafe object ---
    print("\n--- MemoryIsolator Test Case 2: Attempt to access unsafe object ---")
    unsafe_code = "read_from_disk()" # Simplified to ensure 'read_from_disk' is the key identifier
    raised_expected_error = False # Flag to track if the expected error was raised
    try:
        isolator.isolate_code_execution(unsafe_code, safe_memory_context)
        # If this line is reached, no error was raised, which is a test failure.
        print("MemoryIsolator Test 2 Failed: MemoryAccessError was NOT raised for unsafe code.")
        assert False, "MemoryIsolator Test 2 Failed: MemoryAccessError was NOT raised."
    except MemoryAccessError as e:
        # This is the expected path
        raised_expected_error = True
        print(f"Caught expected error: {e}")
        assert "Unauthorized access detected: Code attempts to use 'read_from_disk'" in str(e), "MemoryIsolator Test 2 Failed: Error message mismatch for unsafe access."
        print("MemoryIsolator Test Case 2 Passed.")
    except Exception as e:
        # Catch any other unexpected exceptions
        print(f"MemoryIsolator Test 2 Failed: Caught UNEXPECTED exception of type {type(e).__name__}: {e}")
        assert False, f"MemoryIsolator Test 2 Failed: Caught UNEXPECTED exception: {type(e).__name__}"

    assert raised_expected_error, "MemoryIsolator Test 2 Failed: MemoryAccessError was not caught." # Ensures the except block for MemoryAccessError was indeed hit.

    # --- HeapIsolator Test Cases ---
    print("\n--- Testing HeapIsolator ---")

    # Test H1: Successful allocation and retrieval ---
    print("\n--- Test Case H1: Successful allocation and retrieval ---")
    secret_id = str(uuid.uuid4())
    heap_isolator.allocate_object_to_heap(secret_id, 'sensitive_data', 'my_top_secret_key')
    retrieved_secret = heap_isolator.retrieve_object_from_heap(secret_id, 'sensitive_data')
    assert retrieved_secret == 'my_top_secret_key', "Test H1 Failed: Retrieved value mismatch!"
    print("Test Case H1 Passed: Sensitive data allocated and retrieved correctly.")

    # Test H2: Type error - accessing with wrong expected type ---
    print("\n--- Test Case H2: Type Error (accessing with wrong type) ---")
    try:
        heap_isolator.retrieve_object_from_heap(secret_id, 'temporary_data')
        assert False, "Test H2 Failed: HeapIsolationError (type error) was not raised!"
    except HeapIsolationError as e:
        assert "Type Error:" in str(e), "Test H2 Failed: Error message mismatch for type error!"
        print(f"Caught expected error: {e}")
        print("Test Case H2 Passed: Type error correctly detected.")

    # Test H3: Temporal error - accessing after freeing ---
    print("\n--- Test Case H3: Temporal Error (accessing after freeing) ---")
    temp_data_id = str(uuid.uuid4())
    heap_isolator.allocate_object_to_heap(temp_data_id, 'temporary_data', [1, 2, 3])
    heap_isolator.free_object_from_heap(temp_data_id)
    try:
        heap_isolator.retrieve_object_from_heap(temp_data_id, 'temporary_data')
        assert False, "Test H3 Failed: HeapIsolationError (temporal error) was not raised!"
    except HeapIsolationError as e:
        assert "Temporal Error:" in str(e), "Test H3 Failed: Error message mismatch for temporal error!"
        print(f"Caught expected error: {e}")
        print("Test Case H3 Passed: Temporal error correctly detected.")

    # Test H4: Object not found ---
    print("\n--- Test Case H4: Object not found ---")
    non_existent_id = str(uuid.uuid4())
    try:
        heap_isolator.retrieve_object_from_heap(non_existent_id, 'sensitive_data')
        assert False, "Test H4 Failed: HeapIsolationError (object not found) was not raised!"
    except HeapIsolationError as e:
        assert "Object ID not found" in str(e), "Test H4 Failed: Error message mismatch for object not found!"
        print(f"Caught expected error: {e}")
        print("Test Case H4 Passed: Object not found correctly handled.")

    # Test H5: Attempt to free non-existent object ---
    print("\n--- Test Case H5: Attempt to free non-existent object ---")
    try:
        heap_isolator.free_object_from_heap(non_existent_id)
        assert False, "Test H5 Failed: HeapIsolationError (free non-existent) was not raised!"
    except HeapIsolationError as e:
        assert "Object ID not found to be freed" in str(e), "Test H5 Failed: Error message mismatch!"
        print(f"Caught expected error: {e}")
        print("Test Case H5 Passed: Freeing non-existent object correctly handled.")

    # Test H6: Allocate object to unknown region ---
    print("\n--- Test Case H6: Allocate object to unknown region ---")
    unknown_type_id = str(uuid.uuid4())
    try:
        heap_isolator.allocate_object_to_heap(unknown_type_id, 'unknown_data_type', {'invalid': True})
        assert False, "Test H6 Failed: HeapIsolationError (unknown type) was not raised!"
    except HeapIsolationError as e:
        assert "Unknown object type" in str(e), "Test H6 Failed: Error message mismatch!"
        print(f"Caught expected error: {e}")
        print("Test Case H6 Passed: Unknown region allocation correctly handled.")

    print("\nAll HeapIsolator tests completed successfully!")
