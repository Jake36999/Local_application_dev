"""
Security utilities for input validation and sanitization.
"""
import os
import re
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class SecurityValidator:
    """Handles security validation for user inputs and file operations."""
    
    # Maximum allowed file size (in MB)
    MAX_FILE_SIZE_MB = 500
    
    # Allowed file extensions for scanning
    ALLOWED_EXTENSIONS = {
        '.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.c', '.cs', 
        '.rb', '.go', '.rs', '.php', '.swift', '.kt', '.json', '.yaml', 
        '.yml', '.toml', '.ini', '.md', '.txt', '.html', '.css', '.sql'
    }
    
    @staticmethod
    def validate_directory_path(path: str, must_exist: bool = True) -> Optional[Path]:
        """
        Validate and sanitize a directory path.
        
        Args:
            path: The path to validate
            must_exist: Whether the path must already exist
            
        Returns:
            Validated Path object or None if invalid
        """
        try:
            # Convert to absolute path and resolve
            validated_path = Path(path).resolve()
            
            # Check for path traversal attempts
            if '..' in str(validated_path):
                logger.warning(f"Path traversal attempt detected: {path}")
                return None
            
            # Ensure it's within allowed directories (optional - can be expanded)
            # This prevents scanning system directories
            forbidden_paths = [
                Path('C:\\Windows'),
                Path('C:\\System32'),
                Path('/etc'),
                Path('/sys'),
                Path('/proc')
            ]
            
            for forbidden in forbidden_paths:
                try:
                    validated_path.relative_to(forbidden)
                    logger.warning(f"Attempt to access forbidden directory: {path}")
                    return None
                except ValueError:
                    # Not under forbidden path, continue
                    pass
            
            # Check existence if required
            if must_exist and not validated_path.exists():
                logger.warning(f"Path does not exist: {path}")
                return None
            
            if must_exist and not validated_path.is_dir():
                logger.warning(f"Path is not a directory: {path}")
                return None
                
            return validated_path
            
        except Exception as e:
            logger.error(f"Path validation error: {e}")
            return None
    
    @staticmethod
    def validate_file_path(path: str, must_exist: bool = True) -> Optional[Path]:
        """
        Validate and sanitize a file path.
        
        Args:
            path: The file path to validate
            must_exist: Whether the file must already exist
            
        Returns:
            Validated Path object or None if invalid
        """
        try:
            validated_path = Path(path).resolve()
            
            # Check for path traversal
            if '..' in str(validated_path):
                logger.warning(f"Path traversal attempt in file: {path}")
                return None
            
            # Check file extension
            if validated_path.suffix.lower() not in SecurityValidator.ALLOWED_EXTENSIONS:
                logger.warning(f"Disallowed file extension: {validated_path.suffix}")
                return None
            
            # Check existence and that it's a file
            if must_exist:
                if not validated_path.exists():
                    logger.warning(f"File does not exist: {path}")
                    return None
                if not validated_path.is_file():
                    logger.warning(f"Path is not a file: {path}")
                    return None
                
                # Check file size
                file_size_mb = validated_path.stat().st_size / (1024 * 1024)
                if file_size_mb > SecurityValidator.MAX_FILE_SIZE_MB:
                    logger.warning(f"File too large: {file_size_mb}MB > {SecurityValidator.MAX_FILE_SIZE_MB}MB")
                    return None
            
            return validated_path
            
        except Exception as e:
            logger.error(f"File validation error: {e}")
            return None
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """
        Sanitize user input text.
        
        Args:
            text: The input text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Truncate to max length
        text = text[:max_length]
        
        # Remove potentially dangerous characters
        # Allow alphanumeric, spaces, and common punctuation
        text = re.sub(r'[^\w\s\.\-_,;:()\[\]{}\'\"/?!@#]', '', text)
        
        # Trim whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate a URL for LM Studio connection.
        
        Args:
            url: The URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Allow localhost and private LAN ranges (RFC1918)
        pattern = (
            r'^https?://' 
            r'(' 
            r'localhost|127\.0\.0\.1|'
            r'10\.(?:\d{1,3}\.){2}\d{1,3}|' 
            r'172\.(?:1[6-9]|2\d|3[0-1])\.(?:\d{1,3}\.)\d{1,3}|' 
            r'192\.168\.(?:\d{1,3}\.)\d{1,3}'
            r')' 
            r'(?:\:\d+)?' 
            r'(?:/.*)?$'
        )
        return bool(re.match(pattern, url))
    
    @staticmethod
    def validate_numeric_input(value: str, min_val: float, max_val: float, 
                               default: float) -> float:
        """
        Validate and sanitize numeric input.
        
        Args:
            value: The string value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            default: Default value if invalid
            
        Returns:
            Validated numeric value
        """
        try:
            num = float(value)
            if min_val <= num <= max_val:
                return num
            else:
                logger.warning(f"Numeric value {num} out of range [{min_val}, {max_val}]")
                return default
        except ValueError:
            logger.warning(f"Invalid numeric input: {value}")
            return default
    
    @staticmethod
    def validate_scan_uid(uid: str) -> bool:
        """
        Validate a scan UID format.
        
        Args:
            uid: The UID to validate
            
        Returns:
            True if valid format, False otherwise
        """
        # UID should be alphanumeric, 8-32 characters
        pattern = r'^[a-zA-Z0-9\-]{8,32}$'
        return bool(re.match(pattern, uid))
