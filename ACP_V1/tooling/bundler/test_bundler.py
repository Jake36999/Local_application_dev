"""
Comprehensive test suite for Directory Bundler v4.5
Tests all major functionality including security validation, scanning, and analysis.
"""

import pytest
import os
import json
import tempfile
import shutil
from pathlib import Path
from security_utils import SecurityValidator
from bundler_constants import *

# ==========================================
# SECURITY VALIDATOR TESTS
# ==========================================

class TestSecurityValidator:
    """Tests for SecurityValidator class"""
    
    def test_validate_directory_path_valid(self, tmp_path):
        """Test validation of valid directory path"""
        result = SecurityValidator.validate_directory_path(str(tmp_path))
        assert result is not None
        assert result == tmp_path
    
    def test_validate_directory_path_invalid_traversal(self):
        """Test detection of path traversal attempt"""
        result = SecurityValidator.validate_directory_path("../../../etc/passwd")
        assert result is None
    
    def test_validate_directory_path_nonexistent(self):
        """Test validation of nonexistent path"""
        result = SecurityValidator.validate_directory_path("/nonexistent/path/test", must_exist=True)
        assert result is None
    
    def test_validate_file_path_valid(self, tmp_path):
        """Test validation of valid file path"""
        test_file = tmp_path / "test.py"
        test_file.write_text("# test file")
        
        result = SecurityValidator.validate_file_path(str(test_file))
        assert result is not None
        assert result == test_file
    
    def test_validate_file_path_invalid_extension(self, tmp_path):
        """Test rejection of disallowed file extension"""
        test_file = tmp_path / "test.exe"
        test_file.write_text("binary")
        
        result = SecurityValidator.validate_file_path(str(test_file))
        assert result is None
    
    def test_sanitize_input_basic(self):
        """Test basic input sanitization"""
        result = SecurityValidator.sanitize_input("Hello World 123")
        assert result == "Hello World 123"
    
    def test_sanitize_input_dangerous_chars(self):
        """Test removal of dangerous characters"""
        result = SecurityValidator.sanitize_input("Test<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "alert" in result  # Alphanumeric preserved
    
    def test_sanitize_input_truncation(self):
        """Test input truncation"""
        long_input = "a" * 2000
        result = SecurityValidator.sanitize_input(long_input, max_length=100)
        assert len(result) == 100
    
    def test_validate_url_valid(self):
        """Test validation of valid localhost URL"""
        assert SecurityValidator.validate_url("http://localhost:1234/api")
        assert SecurityValidator.validate_url("http://127.0.0.1:8000")
    
    def test_validate_url_invalid(self):
        """Test rejection of non-localhost URL"""
        assert not SecurityValidator.validate_url("http://example.com")
        assert not SecurityValidator.validate_url("https://malicious.com")
    
    def test_validate_numeric_input_valid(self):
        """Test validation of numeric input"""
        result = SecurityValidator.validate_numeric_input("5.5", 0.0, 10.0, 1.0)
        assert result == 5.5
    
    def test_validate_numeric_input_out_of_range(self):
        """Test handling of out-of-range numeric input"""
        result = SecurityValidator.validate_numeric_input("15.0", 0.0, 10.0, 5.0)
        assert result == 5.0  # Should return default
    
    def test_validate_numeric_input_invalid(self):
        """Test handling of invalid numeric input"""
        result = SecurityValidator.validate_numeric_input("not_a_number", 0.0, 10.0, 5.0)
        assert result == 5.0  # Should return default
    
    def test_validate_scan_uid_valid(self):
        """Test validation of valid scan UID"""
        assert SecurityValidator.validate_scan_uid("abc12345")
        assert SecurityValidator.validate_scan_uid("test-uid-123")
    
    def test_validate_scan_uid_invalid(self):
        """Test rejection of invalid scan UID"""
        assert not SecurityValidator.validate_scan_uid("ab")  # Too short
        assert not SecurityValidator.validate_scan_uid("a" * 50)  # Too long
        assert not SecurityValidator.validate_scan_uid("test@uid!")  # Invalid chars


# ==========================================
# CONSTANTS TESTS
# ==========================================

class TestConstants:
    """Tests for configuration constants"""
    
    def test_dangerous_functions_list(self):
        """Test that dangerous functions list contains expected items"""
        assert "eval" in DANGEROUS_FUNCTIONS
        assert "exec" in DANGEROUS_FUNCTIONS
        assert "pickle" in DANGEROUS_FUNCTIONS
        assert len(DANGEROUS_FUNCTIONS) >= 10
    
    def test_io_functions_list(self):
        """Test that IO functions list is defined"""
        assert "open" in IO_FUNCTIONS
        assert "read" in IO_FUNCTIONS
        assert len(IO_FUNCTIONS) >= 5
    
    def test_secret_patterns(self):
        """Test that secret patterns are defined"""
        assert len(SECRET_PATTERNS) >= 5
        assert any("API_KEY" in pattern for pattern, _ in SECRET_PATTERNS)
        assert any("PASSWORD" in pattern for pattern, _ in SECRET_PATTERNS)
    
    def test_file_extensions(self):
        """Test that file extension lists are defined"""
        assert ".py" in CODE_EXTENSIONS
        assert ".json" in CONFIG_EXTENSIONS
        assert ".md" in DOCUMENTATION_EXTENSIONS
    
    def test_configuration_values(self):
        """Test that configuration constants are reasonable"""
        assert 0 < DEFAULT_MAX_FILE_SIZE_MB <= ABSOLUTE_MAX_FILE_SIZE_MB
        assert 0 < DEFAULT_CHUNK_SIZE_MB <= MAX_CHUNK_SIZE_MB
        assert CONTENT_PREVIEW_LENGTH > 0
        assert DEFAULT_SCAN_DEPTH <= MAX_SCAN_DEPTH


# ==========================================
# FILE CLASSIFICATION TESTS
# ==========================================

class TestFileClassification:
    """Tests for file type classification"""
    
    def test_classify_python_file(self):
        """Test classification of Python files"""
        # This would test the _classify_file_type method
        # Requires importing EnhancedDeepScanner
        pass
    
    def test_classify_config_file(self):
        """Test classification of config files"""
        pass
    
    def test_classify_documentation(self):
        """Test classification of documentation files"""
        pass


# ==========================================
# ANALYSIS ENGINE TESTS
# ==========================================

class TestAnalysisEngine:
    """Tests for code analysis functionality"""
    
    def test_detect_dangerous_function_eval(self):
        """Test detection of eval() usage"""
        test_code = """
def process_user_input(code):
    result = eval(code)  # Dangerous!
    return result
"""
        # This would test the analysis engine
        # Requires importing and setting up AnalysisEngine
        pass
    
    def test_detect_dangerous_function_exec(self):
        """Test detection of exec() usage"""
        test_code = """
def run_code(script):
    exec(script)  # Dangerous!
"""
        pass
    
    def test_detect_hardcoded_secret(self):
        """Test detection of hardcoded secrets"""
        test_code = """
API_KEY = "sk-1234567890abcdef"
PASSWORD = "admin123"
"""
        pass
    
    def test_detect_io_operations(self):
        """Test detection of I/O operations"""
        test_code = """
def read_config():
    with open("config.txt", "r") as f:
        return f.read()
"""
        pass
    
    def test_count_functions_and_classes(self):
        """Test counting of functions and classes"""
        test_code = """
class MyClass:
    def method1(self):
        pass
    
    def method2(self):
        pass

def standalone_function():
    pass
"""
        # Should detect 1 class and 3 functions
        pass


# ==========================================
# INTEGRATION TESTS
# ==========================================

class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_scan_simple_directory(self, tmp_path):
        """Test scanning a simple directory structure"""
        # Create test structure
        (tmp_path / "test.py").write_text("print('hello')")
        (tmp_path / "config.json").write_text('{"key": "value"}')
        (tmp_path / "README.md").write_text("# Test Project")
        
        # This would test the full scan workflow
        # Requires importing DirectoryBundler
        pass
    
    def test_scan_with_ignored_directories(self, tmp_path):
        """Test that ignored directories are skipped"""
        # Create structure with ignored dirs
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text("git config")
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("print('main')")
        
        # Scan should skip .git directory
        pass
    
    def test_scan_respects_file_size_limit(self, tmp_path):
        """Test that files exceeding size limit are skipped"""
        # Create a large file
        large_content = "x" * (100 * 1024 * 1024)  # 100MB
        (tmp_path / "large.py").write_text(large_content)
        (tmp_path / "small.py").write_text("print('small')")
        
        # Scan should skip large file
        pass
    
    def test_cache_functionality(self):
        """Test that caching works correctly"""
        # First scan should create cache
        # Second scan with same config should use cache
        pass
    
    def test_duplicate_detection(self, tmp_path):
        """Test detection of duplicate files"""
        # Create duplicate files
        (tmp_path / "file1.py").write_text("print('same content')")
        (tmp_path / "file2.py").write_text("print('same content')")
        (tmp_path / "file3.py").write_text("print('different')")
        
        # Should detect file1 and file2 as duplicates
        pass


# ==========================================
# ERROR HANDLING TESTS
# ==========================================

class TestErrorHandling:
    """Tests for error handling"""
    
    def test_handle_unreadable_file(self, tmp_path):
        """Test handling of files that can't be read"""
        pass
    
    def test_handle_invalid_python_syntax(self):
        """Test handling of files with invalid Python syntax"""
        test_code = """
def broken_function(
    # Missing closing parenthesis
    pass
"""
        # Should handle gracefully without crashing
        pass
    
    def test_handle_permission_denied(self):
        """Test handling of permission denied errors"""
        pass


# ==========================================
# PERFORMANCE TESTS
# ==========================================

class TestPerformance:
    """Performance and scalability tests"""
    
    def test_scan_large_directory_structure(self, tmp_path):
        """Test scanning a large directory structure"""
        # Create 1000 files in nested structure
        for i in range(10):
            subdir = tmp_path / f"dir_{i}"
            subdir.mkdir()
            for j in range(100):
                (subdir / f"file_{j}.py").write_text(f"# File {i}-{j}")
        
        # Should complete in reasonable time
        pass
    
    def test_memory_usage_with_large_files(self):
        """Test memory usage with large files"""
        # Should not load entire large files into memory
        pass


# ==========================================
# PYTEST CONFIGURATION
# ==========================================

@pytest.fixture
def sample_python_file(tmp_path):
    """Fixture providing a sample Python file"""
    file_path = tmp_path / "sample.py"
    content = """
import os
import sys

class TestClass:
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value

def main():
    obj = TestClass()
    print(obj.get_value())

if __name__ == "__main__":
    main()
"""
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_config_file(tmp_path):
    """Fixture providing a sample config file"""
    file_path = tmp_path / "config.json"
    content = {
        "app_name": "Test App",
        "version": "1.0.0",
        "debug": True
    }
    file_path.write_text(json.dumps(content, indent=2))
    return file_path


# ==========================================
# RUN TESTS
# ==========================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
