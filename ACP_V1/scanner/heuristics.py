
import os
import pathlib
import shutil
import random # Added import for random

def is_binary_file(filepath: pathlib.Path, null_byte_threshold: float = 0.30, scan_bytes: int = 1024) -> bool:
    """
    Detects if a file is likely binary by checking the ratio of null bytes
    in its initial segment. Returns True if binary, False otherwise.
    """
    if not filepath.is_file():
        return False # Not a file, so not a binary file

    try:
        with open(filepath, 'rb') as f:
            initial_bytes = f.read(scan_bytes)

        if not initial_bytes:
            return False # Empty file, not considered binary

        null_byte_count = initial_bytes.count(b'\x00')
        ratio = null_byte_count / len(initial_bytes)

        return ratio > null_byte_threshold
    except Exception as e:
        # Handle cases like permission denied or file not readable
        # print(f"Error reading file {filepath}: {e}")
        return False # Treat unreadable files as not binary for this heuristic

if __name__ == '__main__':
    # --- Test Cases ---
    test_dir = pathlib.Path('./test_heuristics')
    test_dir.mkdir(exist_ok=True)

    # 1. Test with a known text file (expected: False)
    text_file_path = test_dir / 'test_text_file.txt'
    text_content = "This is a sample text file with no null bytes.\nIt should not be detected as binary."
    text_file_path.write_text(text_content)
    print(f"Checking text file '{text_file_path}': {is_binary_file(text_file_path)}")
    assert not is_binary_file(text_file_path), "Text file incorrectly identified as binary!"

    # 2. Test with a simulated binary file (expected: True)
    binary_file_path = test_dir / 'test_binary_file.bin'
    # Modified binary_content to ensure null byte ratio is > 0.30 within scan_bytes
    # Example: 400 null bytes in 1024 bytes -> ratio = 400/1024 = 0.39... > 0.30
    binary_content = b'\x00' * 400 + b'A' * (1024 - 400)
    binary_file_path.write_bytes(binary_content)
    print(f"Checking binary file '{binary_file_path}': {is_binary_file(binary_file_path)}")
    assert is_binary_file(binary_file_path), "Binary file incorrectly identified as text!"

    # 3. Test with a file below threshold (expected: False)
    low_null_file_path = test_dir / 'low_null_file.dat'
    low_null_content = b'\x00' * 100 + b'A' * 900 # 10% null bytes (100/1000 = 0.1)
    # Ensure content length is at least scan_bytes for accurate ratio calculation
    if len(low_null_content) < 1024:
        low_null_content += b'B' * (1024 - len(low_null_content))
    low_null_file_path.write_bytes(low_null_content)
    print(f"Checking low null file '{low_null_file_path}': {is_binary_file(low_null_file_path)}")
    assert not is_binary_file(low_null_file_path), "Low null file incorrectly identified as binary!"

    # 4. Test with an empty file (expected: False)
    empty_file_path = test_dir / 'empty_file.txt'
    empty_file_path.touch()
    print(f"Checking empty file '{empty_file_path}': {is_binary_file(empty_file_path)}")
    assert not is_binary_file(empty_file_path), "Empty file incorrectly identified as binary!"

    # 5. Test with a non-existent file (expected: False)
    non_existent_file_path = test_dir / 'non_existent.txt'
    print(f"Checking non-existent file '{non_existent_file_path}': {is_binary_file(non_existent_file_path)}")
    assert not is_binary_file(non_existent_file_path), "Non-existent file incorrectly identified as binary!"

    print("\nAll heuristic binary detection tests passed successfully!")

    # --- Cleanup ---
    shutil.rmtree(test_dir)
