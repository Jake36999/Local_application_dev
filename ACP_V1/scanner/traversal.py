
import pathlib
import os
import shutil # Added import for shutil

EXCLUDED_DIRS = {'.git', 'node_modules', '.venv'}

def traverse_directory(path):
    """
    Recursively traverses a directory, yielding all file paths while skipping
    specified noise directories with case-insensitive matching.
    """
    base_path = pathlib.Path(path)
    if not base_path.is_dir():
        raise ValueError(f"Path is not a directory: {path}")

    # Use a stack for iterative deepening to avoid recursion depth limits
    # and ensure O(N) efficiency by processing each directory/file once.
    stack = [base_path]

    while stack:
        current_dir = stack.pop()

        # Pre-scan filtering for noise directories
        dir_name_lower = current_dir.name.lower()
        if dir_name_lower in EXCLUDED_DIRS:
            # print(f"Skipping excluded directory: {current_dir}") # Commented out for cleaner output in real runs
            continue

        try:
            for entry in current_dir.iterdir():
                if entry.is_dir():
                    stack.append(entry) # Add directories to stack for later processing
                else:
                    yield entry # Yield files directly
        except PermissionError:
            # print(f"Permission denied for directory: {current_dir}. Skipping.")
            continue
        except Exception as e:
            # print(f"Error traversing {current_dir}: {e}. Skipping.")
            continue

if __name__ == '__main__':
    # Example Usage:
    # Create some dummy directories and files for testing
    test_root = pathlib.Path('./test_project')

    # Ensure a clean slate for testing
    if test_root.exists():
        shutil.rmtree(test_root)

    test_root.mkdir(exist_ok=True)
    (test_root / 'file1.txt').write_text('content')
    (test_root / 'subdir').mkdir(exist_ok=True)
    (test_root / 'subdir' / 'file2.py').write_text('print("hello")')
    (test_root / '.git').mkdir(exist_ok=True)
    (test_root / '.git' / 'config').write_text('[core]')
    (test_root / 'node_modules').mkdir(exist_ok=True)
    (test_root / 'node_modules' / 'package.js').write_text('module')
    (test_root / 'AnotherSubDir').mkdir(exist_ok=True)
    (test_root / 'AnotherSubDir' / 'FILE3.md').write_text('markdown')
    (test_root / 'NODE_MODULES_CASE_INSENSITIVE').mkdir(exist_ok=True)
    (test_root / '.venv').mkdir(exist_ok=True)
    (test_root / '.venv' / 'activate').write_text('source')
    # Fix: Create 'SUBDIR' before trying to write a file into it
    (test_root / 'SUBDIR').mkdir(exist_ok=True)
    (test_root / 'SUBDIR' / 'another_file.txt').write_text('more content')

    print('\nTraversing test_project directory:') # Using single quotes and explicit newline escape
    found_files = []
    for f_path in traverse_directory(test_root):
        found_files.append(str(f_path))
        print(f_path)

    expected_files = {
        str(test_root / 'file1.txt'),
        str(test_root / 'subdir' / 'file2.py'),
        str(test_root / 'AnotherSubDir' / 'FILE3.md'),
        str(test_root / 'SUBDIR' / 'another_file.txt')
    }

    assert set(found_files) == expected_files, f"Expected {expected_files}, but got {set(found_files)}"
    print('\nTest traversal successful! Correct files found and excluded directories skipped.') # Using single quotes and explicit newline escape

    # Clean up test files
    shutil.rmtree(test_root)

