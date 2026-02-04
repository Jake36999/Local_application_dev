"""
Helper script to create test file with comment directives for Phase 5 testing.
"""

code = '''# @extract
# @pure
def calculate(x: int) -> int:
    """Pure computation function."""
    return x * 2

# @io_boundary
def save_result(value):
    """Writes to disk."""
    with open('result.txt', 'w') as f:
        f.write(str(value))

# @extract
# @service_candidate
class Calculator:
    """Stateless calculator service."""
    
    def add(self, a: int, b: int) -> int:
        return a + b
    
    def multiply(self, a: int, b: int) -> int:
        return a * b

# @do_not_extract
def internal_helper():
    """Internal implementation detail."""
    pass
'''

with open('test_directives.py', 'w') as f:
    f.write(code)

print("[+] Created test_directives.py")
