
import sys
import importlib

MIN_PYTHON_VERSION = (3, 10)
REQUIRED_LIBS = ['pathlib', 'ast', 'hashlib']

def check_python_version():
    if sys.version_info < MIN_PYTHON_VERSION:
        print(f"Error: Python version {sys.version.split(' ')[0]} detected. Required Python version is {'.'.join(map(str, MIN_PYTHON_VERSION))} or higher.")
        sys.exit(11)
    print(f"Python version check passed: {sys.version.split(' ')[0]} >= {'.'.join(map(str, MIN_PYTHON_VERSION))}")

def check_stdlib_integrity():
    for lib_name in REQUIRED_LIBS:
        try:
            importlib.import_module(lib_name)
            print(f"Standard library '{lib_name}' check passed.")
        except ImportError:
            print(f"Error: Standard library '{lib_name}' could not be imported. It might be missing or corrupted.")
            sys.exit(12)
        except Exception as e:
            print(f"Error: An unexpected error occurred while checking standard library '{lib_name}': {e}")
            sys.exit(12)
    print("All required standard libraries are available and appear intact.")

if __name__ == '__main__':
    print("Starting environment bootstrapping (R2 Verification)...")
    check_python_version()
    check_stdlib_integrity()
    print("Environment bootstrapping complete: All checks passed successfully.")
