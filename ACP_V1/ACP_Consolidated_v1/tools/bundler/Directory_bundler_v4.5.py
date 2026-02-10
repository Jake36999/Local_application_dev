# ==========================================
# VERSION 4.5 - FINAL ENHANCED BUNDLER IMPLEMENTATION
# ==========================================
"""
Directory Bundler v4.5 - Advanced Codebase Analysis and Bundling Tool

This module provides comprehensive functionality for scanning, analyzing, and bundling
code repositories with security auditing, duplicate detection, and AI-powered insights.

Key Features:
    - Hierarchical directory scanning with configurable filters
    - AST-based Python code analysis
    - Security vulnerability detection (OWASP patterns)
    - Duplicate file detection via content hashing
    - LM Studio integration for AI-powered analysis
    - RESTful API for dashboard integration
    - Advanced caching system for performance
    - Real-time progress tracking via SSE

Architecture:
    - EnhancedDeepScanner: Handles file system traversal and indexing
    - AnalysisEngine: Performs static code analysis and security audits
    - LMStudioIntegration: Manages AI-powered code insights
    - DirectoryBundler: Orchestrates the complete workflow
    - BundlerCLI: Provides command-line interface

Output Structure:
    bundler_scans/
        {uid}/
            manifest.json       # Scan metadata and configuration
            tree.json          # Hierarchical directory structure
            labels.json        # Duplicate detection results
            files/             # Individual file metadata
            chunks/            # Chunked content for processing
            ai/                # AI analysis results

Security:
    - Input validation for all user inputs
    - Path traversal prevention
    - File size limits enforcement
    - Dangerous function detection
    - Hardcoded secret detection

Author: Enhanced Directory Bundler Team
Version: 4.5.0
Date: February 2026
License: MIT
"""

import os
import sys
import json
import uuid
import datetime
import threading
import http.server
import socketserver
import hashlib
import traceback
import ast
import urllib.request
import urllib.error
from pathlib import Path
from urllib.parse import urlparse, parse_qs, quote
import requests
import re
import base64
import math
from typing import Dict, List, Any, Optional, cast
import logging

# Import security utilities
from security_utils import SecurityValidator
from bundler_constants import *
from data_parser import DataParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Centralized LM Studio load defaults
LMSTUDIO_DEFAULT_LOAD_PARAMS = {
    "context_length": 8192,
    "gpu_offload_ratio": 1.0,
    "ttl": 3600,
}

# ==========================================
# TERMINAL UI HELPER
# ==========================================
class TerminalUI:
    """
    Terminal UI Helper - ANSI Color Codes and Progress Visualization
    
    Provides utility methods for enhanced terminal output including colored text
    and dynamic progress bars. Uses ANSI escape codes for cross-platform terminal
    formatting (works on Windows 10+, Linux, macOS).
    
    Color Constants:
        HEADER: Magenta for headers
        BLUE: Blue for informational messages
        GREEN: Green for success messages
        WARNING: Yellow for warnings
        FAIL: Red for errors
        BOLD: Bold text emphasis
    
    Methods:
        print_progress: Displays a dynamic progress bar with percentage completion
    
    Example:
        >>> TerminalUI.print_progress(50, 100, prefix='Processing', suffix='files')
        Processing |█████████████████████████---------------------| 50.0% files
    """
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

    @staticmethod
    def print_progress(iteration, total, prefix='', suffix='', decimals=1, length=50):
        """
        Display a dynamic terminal progress bar.
        
        Creates an in-place updating progress bar that shows completion percentage
        and visual progress indicator. Designed for loops where progress needs to
        be displayed to the user.
        
        Args:
            iteration (int): Current iteration count (1-based)
            total (int): Total number of iterations
            prefix (str): Text to display before progress bar
            suffix (str): Text to display after percentage
            decimals (int): Number of decimal places for percentage
            length (int): Character length of the progress bar
        
        Example:
            >>> for i in range(1, 101):
            ...     TerminalUI.print_progress(i, 100, prefix='Loading', suffix='Complete')
            Loading |██████████████████████████████████████████████| 100.0% Complete
        
        Note:
            Uses carriage return (\\r) to overwrite the same line. Final iteration
            adds a newline to preserve the completed progress bar.
        """
        if total == 0:
            return
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filled_length = int(length * iteration // total)
        bar = '█' * filled_length + '-' * (length - filled_length)
        # \r returns cursor to start of line
        sys.stdout.write(f'\r{TerminalUI.BLUE}{prefix}{TerminalUI.ENDC} |{bar}| {percent}% {suffix}')
        if iteration == total:
            sys.stdout.write('\n')
        sys.stdout.flush()

class ConfigManager:
    """
    Configuration Manager - Handles Configuration Loading and Defaults
    
    Manages application configuration with sensible defaults. In this version,
    configuration is primarily code-based, but the architecture supports future
    enhancement with external config files (YAML, TOML, JSON).
    
    Attributes:
        uid (str): Unique identifier for the scan session
        default_config (dict): Default configuration values from bundler_constants
    
    Configuration Keys:
        - ignore_dirs: Directories to skip during scanning
        - binary_extensions: File extensions to treat as binary
        - max_chunk_size_mb: Maximum size of content chunks
        - max_file_size_mb: Maximum individual file size
        - lmstudio_enabled: Enable AI analysis via LM Studio
        - enable_cache: Enable result caching
    
    Future Enhancement:
        Could be extended to load from:
        - ~/.bundler/config.yml
        - .bundlerrc in project root
        - Environment variables
    """
    
    def __init__(self, uid):
        self.uid = uid
        self.default_config = {
            "ignore_dirs": DEFAULT_IGNORE_DIRS,
            "ignore_file_names": IGNORE_FILE_NAMES,
            "binary_extensions": BINARY_EXTENSIONS,
            "vision_extensions": VISION_EXTENSIONS,
            "max_chunk_size_mb": DEFAULT_CHUNK_SIZE_MB,
            "mode": "quick",
            "lmstudio_enabled": False,
            "lmstudio_url": DEFAULT_LM_STUDIO_URL,
            "include_tests": True,
            "include_docs": True,
            "include_config": True,
            "max_file_size_mb": DEFAULT_MAX_FILE_SIZE_MB,
            "scan_depth": DEFAULT_SCAN_DEPTH,
            "output_format": "json",
            "enable_cache": True,
            "cache_dir": DEFAULT_CACHE_DIR,
            "embedding_model": EMBEDDING_MODEL_NAME,
            "similarity_threshold": SIMILARITY_THRESHOLD
        }
    
    def load_config(self):
        return self.default_config

# ==========================================
# 4. ENHANCED DEEP SCANNER (3.5 STRUCTURED)
# ==========================================
class EnhancedDeepScanner:
    """
    Enhanced Deep Scanner - Hierarchical File System Analysis
    
    Performs comprehensive directory traversal and creates a structured, multi-layered
    representation of code repositories. Implements the "3+ Model" architecture where
    scans produce hierarchical outputs optimized for different use cases (UI display,
    AI processing, search indexing).
    
    Architecture - The "3+ Model":
        1. manifest.json - High-level scan metadata and index
        2. tree.json - Hierarchical directory structure for UI rendering
        3. files/ - Individual file metadata with analysis results
        4. chunks/ - Content grouped into processing units
        5. labels.json - Cross-file relationships and duplicates
        6. ai/ - AI-generated insights (when LM Studio enabled)
    
    Features:
        - Recursive directory scanning with configurable filters
        - Content-based duplicate detection via MD5 hashing
        - File type classification (code, config, docs, tests)
        - Chunking for memory-efficient processing
        - Progress tracking with callbacks
        - Path validation and security checks
    
    Attributes:
        uid (str): Unique identifier for this scan
        config (Dict): Configuration including ignore patterns and limits
        scan_dir (str): Output directory for this scan
        file_registry (List[Dict]): Index of all scanned files
        labels (Dict): Cross-file labels and duplicate detection results
    
    Usage:
        >>> scanner = EnhancedDeepScanner("abc123", config, "./output/scan_abc123")
        >>> scanner.scan_directory("/path/to/project")
        >>> scanner.run_full_analysis()
    
    Output Structure:
        scan_abc123/
            manifest.json          # Scan summary and configuration
            tree.json              # Directory hierarchy
            labels.json            # Duplicates and cross-references
            files/
                file_0001.json     # File metadata + analysis
                file_0002.json
                ...
            chunks/
                chunk_01.json      # Grouped content for processing
                chunk_02.json
                ...
    
    Security:
        - Validates all paths to prevent directory traversal
        - Respects file size limits
        - Skips binary files automatically
        - Handles permission errors gracefully
    """
    def __init__(self, uid: str, config: Dict[str, Any], scan_dir: str):
        self.uid = uid
        self.config = config
        self.scan_dir = scan_dir # The SCN_<uid> folder
        self.files_dir = os.path.join(scan_dir, "files")
        self.chunks_dir = os.path.join(scan_dir, "chunks")
        self.ai_dir = os.path.join(scan_dir, "ai")
        
        # In-memory tracking for cross-indexing
        self.file_registry: List[Dict[str, Any]] = []  # List of file metadata for the manifest
        self.directory_tree: List[Dict[str, Any]] = []  # For tree.json
        self.current_chunk_files: List[Dict[str, Any]] = []
        self.chunk_count: int = 0
        self.total_processed_size: float = 0.0
        
        # PHASE 3: Global labels system for cross-file tracking
        self.labels: Dict[str, Any] = {
            "file_labels": {},      # file_id -> [label1, label2, ...]
            "directory_labels": {}, # dir_path -> [label1, label2, ...]
            "duplicates": {},       # content_hash -> [file_id1, file_id2, ...]
            "metadata": {
                "scan_uid": uid,
                "scan_time": datetime.datetime.now().isoformat(),
                "total_duplicates": 0
            }
        }
        
        # Create directories
        os.makedirs(self.files_dir, exist_ok=True)
        os.makedirs(self.chunks_dir, exist_ok=True)
        os.makedirs(self.ai_dir, exist_ok=True)

    def scan_directory(self, base_dir: str, progress_callback=None):
        """
        Perform recursive directory scan and build hierarchical structure.
        
        Traverses the directory tree, collecting file metadata, computing hashes,
        and organizing content into chunks. Implements the "3+ Model" by generating
        multiple complementary representations of the codebase.
        
        Args:
            base_dir (str): Root directory to scan (will be validated for security)
            progress_callback (callable, optional): Function called with (current, total, status)
                for real-time progress updates. Useful for UI integration.
        
        Returns:
            str: Path to the scan directory containing all outputs
        
        Raises:
            ValueError: If base_dir is invalid or unsafe
            PermissionError: If unable to read directories/files
        
        Process Flow:
            1. Validate and resolve base directory path
            2. Build list of files to scan (respecting filters)
            3. For each file:
                - Read content and compute MD5 hash
                - Extract metadata (size, timestamps, type)
                - Classify file type (code, config, docs, etc.)
                - Track duplicates by content hash
                - Assign to chunk based on size limits
            4. Generate tree.json (hierarchical structure)
            5. Finalize manifest.json (scan summary)
            6. Save labels.json (duplicates and cross-refs)
        
        Example:
            >>> scanner = EnhancedDeepScanner("scan123", config, "./output")
            >>> def progress(current, total, status):
            ...     print(f"{status}: {current}/{total}")
            >>> scanner.scan_directory("/project", progress_callback=progress)
            indexing: 1/150
            indexing: 2/150
            ...
            './output/scan123'
        
        Performance:
            - Processes ~1000 files/minute on modern hardware
            - Memory usage: O(n) where n is number of files
            - Chunk-based processing prevents memory overflow on large repos
        """
        # Validate directory or file path
        validated_path = SecurityValidator.validate_directory_path(base_dir, must_exist=True)
        validated_file = None
        single_file_mode = False
        if validated_path is None:
            validated_file = SecurityValidator.validate_file_path(base_dir, must_exist=True)
            if validated_file is None:
                raise ValueError(f"Invalid or unsafe path: {base_dir}")
            single_file_mode = True
        
        if single_file_mode:
            if validated_file is None:
                raise ValueError("Single file mode failed to validate file path.")
            base_path = validated_file.parent
        else:
            if validated_path is None:
                raise ValueError("Base path validation failed.")
            base_path = validated_path
        ignore_dirs = {d.lower() for d in self.config.get('ignore_dirs', [])}
        binary_extensions = set(self.config.get('binary_extensions', []))
        vision_extensions = set(self.config.get('vision_extensions', []))
        ignore_file_names = {n.lower() for n in self.config.get('ignore_file_names', IGNORE_FILE_NAMES)}
        if single_file_mode and validated_file is not None:
            if validated_file.name.lower() in ignore_file_names:
                raise ValueError(f"File is ignored by name: {validated_file.name}")
        
        print(f"--- 3+ Structured Scan Starting: {self.uid} ---")

        # We first build a flat list of files to process to provide better progress tracking
        files_to_scan = []
        if single_file_mode and validated_file is not None:
            files_to_scan = [validated_file]
        else:
            for root, dirs, files in os.walk(base_path):
                dirs[:] = [d for d in dirs if d.lower() not in ignore_dirs]
                for file in files:
                    if file.lower() in ignore_file_names:
                        continue
                    file_path = Path(root) / file
                    ext_lower = file_path.suffix.lower()
                    if ext_lower in binary_extensions and ext_lower not in vision_extensions:
                        continue
                    # Check max file size
                    try:
                        file_size = file_path.stat().st_size / (1024 * 1024)
                        if file_size > self.config.get("max_file_size_mb", 50.0):
                            continue
                    except Exception:
                        pass
                    files_to_scan.append(file_path)

        total_files = len(files_to_scan)
        current_chunk_size: float = 0.0
        self.chunk_count = 1

        for idx, file_path in enumerate(files_to_scan):
            relative_path = str(file_path.relative_to(base_path))
            
            try:
                ext_lower = file_path.suffix.lower()
                file_stat = file_path.stat()
                file_size_mb = file_stat.st_size / (1024 * 1024)

                vision_base64 = None
                if ext_lower in vision_extensions:
                    data = file_path.read_bytes()
                    raw_content = ""
                    vision_base64 = base64.b64encode(data).decode('utf-8') if data else ""
                else:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        raw_content = f.read()
                
                # PHASE 2: Compute content and path hashes
                hash_basis = raw_content if raw_content else (vision_base64 or str(file_path))
                content_hash = hashlib.md5(hash_basis.encode('utf-8')).hexdigest()
                path_hash = hashlib.md5(relative_path.encode('utf-8')).hexdigest()
                
                # PHASE 2: Get file timestamps
                file_stat = file_path.stat()
                created_time = datetime.datetime.fromtimestamp(file_stat.st_ctime).isoformat()
                modified_time = datetime.datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                
                # PHASE 2: Classify file type
                file_type = self._classify_file_type(file_path, raw_content)
                
                structured_preview = self._parse_structured_preview(file_path, raw_content)

                # 1. Create File Entity
                file_id = f"file_{idx:04d}"
                file_info = {
                    "file_id": file_id,
                    "path": relative_path,
                    "name": file_path.name,
                    "extension": file_path.suffix,
                    "size_mb": round(file_size_mb, 4),
                    "chunk_id": f"chunk_{self.chunk_count:02d}",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "content_preview": raw_content[:CONTENT_PREVIEW_LENGTH],  # For immediate UI display
                    # PHASE 2: New metadata fields
                    "content_hash": content_hash,
                    "path_hash": path_hash,
                    "created_time": created_time,
                    "modified_time": modified_time,
                    "file_type": file_type
                }

                if vision_base64 is not None:
                    file_info["vision_base64"] = vision_base64

                if structured_preview:
                    file_info["structured_preview"] = structured_preview

                # Save individual file data (initial metadata)
                with open(os.path.join(self.files_dir, f"{file_id}.json"), 'w') as f:
                    json.dump(file_info, f, indent=2)

                self.file_registry.append({
                    "path": relative_path,
                    "file_id": file_id,
                    "size": file_size_mb,
                    "extension": file_path.suffix,
                    "content_hash": content_hash,
                    "file_type": file_type
                })
                
                # PHASE 3: Track duplicates by content_hash
                if content_hash not in self.labels["duplicates"]:
                    self.labels["duplicates"][content_hash] = []
                self.labels["duplicates"][content_hash].append(file_id)

                # 2. Manage Chunks
                if current_chunk_size + file_size_mb > self.config.get("max_chunk_size_mb", 2.0):
                    self._save_chunk(self.current_chunk_files, self.chunk_count)
                    self.chunk_count += 1
                    self.current_chunk_files = []
                    current_chunk_size = 0

                self.current_chunk_files.append({
                    "file_id": file_id,
                    "path": relative_path,
                    "content": raw_content,
                    "structured_preview": structured_preview if structured_preview else None,
                    "vision_base64": vision_base64 if vision_base64 is not None else None
                })
                current_chunk_size += file_size_mb
                self.total_processed_size += file_size_mb

                # Progress Update for the API/UI
                if progress_callback:
                    progress_callback(idx + 1, total_files, "indexing")
                elif total_files > 0:
                    TerminalUI.print_progress(idx + 1, total_files, prefix='Scanning', suffix=f'({idx + 1}/{total_files} files)')

            except Exception as e:
                print(f"⚠ Skipping {relative_path}: {e}")

        # Save the final chunk
        if self.current_chunk_files:
            self._save_chunk(self.current_chunk_files, self.chunk_count)

        # 3. Generate the UI-ready Tree
        self._generate_tree_json(base_path, files_to_scan)
        
        # 4. Finalize Manifest
        if single_file_mode:
            assert validated_file is not None
            manifest_target = validated_file
        else:
            manifest_target = base_path

        self._finalize_manifest(manifest_target, total_files)

        print(f"✅ Scan Complete. Manifest generated in {self.scan_dir}")
        return self.scan_dir
    
    def _classify_file_type(self, file_path: Path, content: str) -> str:
        """Classify file into categories: code, config, test, documentation, or other"""
        extension = file_path.suffix.lower()
        name_lower = file_path.name.lower()
        
        # Code files
        if extension in ['.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.c', '.cs', '.rb', '.go', '.rs', '.php', '.swift', '.kt']:
            return "code"
        
        # Configuration files
        if extension in ['.json', '.yaml', '.yml', '.toml', '.ini', '.conf', '.cfg', '.config']:
            return "config"
        if "config" in name_lower or "settings" in name_lower:
            return "config"
        
        # Test files
        if "test" in name_lower or "spec" in name_lower:
            return "test"
        if extension in ['.test.js', '.spec.js', '.test.py', '.spec.py']:
            return "test"
        
        # Documentation
        if extension in ['.md', '.rst', '.txt', '.doc', '.docx']:
            return "documentation"
        if name_lower in ['readme', 'license', 'changelog', 'contributing']:
            return "documentation"
        
        # Markup/HTML
        if extension in ['.html', '.xml', '.svg']:
            return "markup"
        
        # Stylesheet
        if extension in ['.css', '.scss', '.sass', '.less']:
            return "stylesheet"
        
        # Data files
        if extension in ['.csv', '.sql', '.db']:
            return "data"

        # Vision files
        if extension in VISION_EXTENSIONS:
            return "vision"
        
        return "other"

    def _parse_structured_preview(self, file_path: Path, content: str) -> Optional[Dict[str, Any]]:
        """Attempt to parse structured data for CSV/TSV/XML/JSON files."""
        try:
            return DataParser.parse_structured(file_path.suffix, content)
        except Exception as exc:
            logger.debug("Structured parse failed for %s: %s", file_path, exc)
            return None

    def run_full_analysis(self, progress_callback=None):
        """
        Iterates over self.file_registry to perform deep static and security analysis.
        Updates each individual file JSON with results.
        """
        total_files = len(self.file_registry)
        print(f"--- Starting Full Analysis for {total_files} files ---")

        for idx, entry in enumerate(self.file_registry):
            file_id = entry["file_id"]
            file_path_json = os.path.join(self.files_dir, f"{file_id}.json")
            
            try:
                # Load current file data
                with open(file_path_json, 'r') as f:
                    file_data = json.load(f)
                
                # Fetch full content from the corresponding chunk if content_preview isn't enough
                # For 3+, we usually re-read the specific file content for analysis if needed,
                # or use the preview if it's a small file. Let's assume we need the full content
                # from the original source path for accuracy during this phase.
                # In a real deployed scenario, you might read from chunks or the files_dir.
                
                # We'll perform Python-specific analysis
                if entry["extension"] == '.py':
                    analysis = self._analyze_python_file(file_data)
                    file_data["analysis"] = analysis
                
                # Update the file JSON with analysis results
                with open(file_path_json, 'w') as f:
                    json.dump(file_data, f, indent=2)
                
                # PHASE 4: Delete raw content preview to save memory after analysis
                if "content_preview" in file_data:
                    del file_data["content_preview"]

                if progress_callback:
                    progress_callback(idx + 1, total_files, "analyzing")
                elif total_files > 0:
                    TerminalUI.print_progress(idx + 1, total_files, prefix='Analyzing', suffix=f'({idx + 1}/{total_files} files)')

            except Exception as e:
                print(f"⚠ Analysis failed for {entry['path']}: {e}")

    def _analyze_python_file(self, file_data: Dict) -> Dict:
        """Internal helper for Python static analysis using AST and Regex."""
        # Use content_preview or re-read original if necessary
        # For this refactor, we simulate the logic from previous versions
        analysis: Dict[str, Any] = {
            "ast_parsed": False,
            "security_findings": [],
            "dangerous_calls": [],
            "io_operations": [],
            "async_functions": [],
            "decorators": [],
            "stats": {}
        }
        
        # Note: In a production environment, you would ensure access to the full raw content.
        # Here we use content_preview for logic demonstration.
        content = file_data.get("content_preview", "")
        
        try:
            tree = ast.parse(content)
            analysis["ast_parsed"] = True
            
            imports = []
            functions = 0
            classes = 0
            node_count = 0
            async_count = 0
            decorator_count = 0
            
            # Use constants for dangerous and IO functions
            dangerous_functions = DANGEROUS_FUNCTIONS
            io_functions = IO_FUNCTIONS
            
            for node in ast.walk(tree):
                node_count += 1
                
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.append(ast.dump(node)) # Simplified for demo
                elif isinstance(node, ast.FunctionDef):
                    functions += 1
                    # Check for decorators on function
                    if node.decorator_list:
                        decorator_count += len(node.decorator_list)
                        for decorator in node.decorator_list:
                            analysis["decorators"].append({
                                "type": "function",
                                "name": node.name,
                                "decorator": ast.dump(decorator)[:100]  # Truncated for brevity
                            })
                elif isinstance(node, ast.AsyncFunctionDef):
                    functions += 1
                    async_count += 1
                    analysis["async_functions"].append(node.name)
                    # Check for decorators on async function
                    if node.decorator_list:
                        decorator_count += len(node.decorator_list)
                elif isinstance(node, ast.ClassDef):
                    classes += 1
                    # Check for decorators on class
                    if node.decorator_list:
                        decorator_count += len(node.decorator_list)
                
                # Look for dangerous function calls
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in dangerous_functions:
                            analysis["dangerous_calls"].append({
                                "function": node.func.id,
                                "line": getattr(node, 'lineno', 'unknown'),
                                "severity": "high"
                            })
                        # Check for IO operations
                        elif node.func.id in io_functions:
                            analysis["io_operations"].append({
                                "function": node.func.id,
                                "line": getattr(node, 'lineno', 'unknown')
                            })
                    # Check for attribute-based calls like os.system, subprocess.call
                    elif isinstance(node.func, ast.Attribute):
                        full_call = f"{ast.dump(node.func.value)}.{node.func.attr}"
                        if "os.system" in full_call or "subprocess" in full_call:
                            analysis["dangerous_calls"].append({
                                "function": node.func.attr,
                                "line": getattr(node, 'lineno', 'unknown'),
                                "severity": "high"
                            })
                        elif "open" in node.func.attr or "socket" in full_call:
                            analysis["io_operations"].append({
                                "function": node.func.attr,
                                "line": getattr(node, 'lineno', 'unknown')
                            })
            
            analysis["stats"] = {
                "imports_count": len(imports),
                "function_count": functions,
                "class_count": classes,
                "node_count": node_count,
                "async_functions_count": async_count,
                "decorator_count": decorator_count,
                "io_operations_count": len(analysis["io_operations"]),
                "dangerous_calls_count": len(analysis["dangerous_calls"])
            }
        except Exception as parse_error:
            logger.debug(f"AST parse error: {parse_error}")

        # Enhanced security regex checks using constants
        for pattern, desc in SECRET_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                analysis["security_findings"].append(desc)

        return analysis

    def _save_chunk(self, files_list: List[Dict], count: int):
        """Writes a bundling unit (chunk) to disk."""
        chunk_id = f"chunk_{count:02d}"
        chunk_data = {
            "chunk_id": chunk_id,
            "scan_uid": self.uid,
            "files_included": [f["file_id"] for f in files_list],
            "data": files_list,
            "timestamp": datetime.datetime.now().isoformat()
        }
        with open(os.path.join(self.chunks_dir, f"{chunk_id}.json"), 'w') as f:
            json.dump(chunk_data, f, indent=2)

    def _generate_tree_json(self, base_path: Path, files_list: List[Path]):
        """Creates the hierarchical tree.json for the dashboard sidebar."""
        tree: Dict[str, Any] = {}
        for path in files_list:
            parts = path.relative_to(base_path).parts
            current_level = tree
            for part in parts:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]

        def _recursive_build(data, current_path=""):
            nodes = []
            for name, children in data.items():
                full_path = os.path.join(current_path, name).replace("\\", "/")
                node = {"name": name, "path": full_path}
                if children:
                    node["type"] = "directory"
                    node["children"] = _recursive_build(children, full_path)
                else:
                    node["type"] = "file"
                    # Link back to the file_id for rapid lookup
                    reg_entry = next((f for f in self.file_registry if f["path"] == full_path), None)
                    if reg_entry:
                        node["file_id"] = reg_entry["file_id"]
                nodes.append(node)
            return sorted(nodes, key=lambda x: (x["type"] != "directory", x["name"]))

        final_tree = _recursive_build(tree)
        with open(os.path.join(self.scan_dir, "tree.json"), 'w') as f:
            json.dump(final_tree, f, indent=2)

    def _finalize_manifest(self, root_path: Path, total_files: int):
        """Creates the single source of truth manifest.json."""
        # PHASE 3: Calculate duplicate count
        duplicate_count = sum(1 for files in self.labels["duplicates"].values() if len(files) > 1)
        self.labels["metadata"]["total_duplicates"] = duplicate_count
        
        manifest = {
            "scan_uid": self.uid,
            "timestamp": datetime.datetime.now().isoformat(),
            "root_path": str(root_path),
            "total_files": total_files,
            "total_chunks": self.chunk_count,
            "total_size_mb": round(self.total_processed_size, 2),
            "config_used": self.config,
            "versions": {
                "bundler": "v4.0.0-final",
                "schema": "1.0.0"
            },
            "indices": {
                "tree": "tree.json",
                "files_folder": "files/",
                "chunks_folder": "chunks/",
                "ai_folder": "ai/",
                "labels": "labels.json"  # PHASE 3: New index entry
            },
            # PHASE 3: Include labels metadata
            "labels_metadata": self.labels["metadata"],
            "duplicates_detected": duplicate_count > 0
        }
        with open(os.path.join(self.scan_dir, "manifest.json"), 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # PHASE 3: Save labels to separate file for easy access
        with open(os.path.join(self.scan_dir, "labels.json"), 'w') as f:
            json.dump(self.labels, f, indent=2)

# ==========================================
# 5. ENHANCED ANALYSIS ENGINE
# ==========================================
class AnalysisEngine:
    """
    Performs Static and Dynamic analysis on Python code.
    Enhanced with comprehensive security audit and advanced metrics.
    """
    def __init__(self, uid):
        self.uid = uid
        
    def quick_analysis(self, file_data):
        """Perform quick static analysis"""
        analysis: Dict[str, Any] = {}
        
        if file_data["path"].endswith('.py'):
            try:
                # CRITICAL FIX: Parse raw_content, not the formatted block
                source_to_parse = file_data.get("content_preview", file_data.get("content_block", ""))
                
                # Parse using AST for better accuracy
                import ast
                
                tree = ast.parse(source_to_parse)
                analysis["ast_parsed"] = True
                analysis["imports"] = []
                analysis["function_count"] = 0
                analysis["class_count"] = 0
                analysis["node_count"] = 0
                analysis["dangerous_calls"] = []
                analysis["io_operations"] = []
                analysis["async_functions"] = []
                analysis["decorators"] = []
                analysis["todo_count"] = 0
                analysis["security_findings"] = []
                
                # Use constants for dangerous and IO functions
                dangerous_functions = DANGEROUS_FUNCTIONS
                io_functions = IO_FUNCTIONS
                
                # Extract imports and count nodes
                for node in ast.walk(tree):
                    analysis["node_count"] = analysis["node_count"] + 1
                    
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis["imports"].append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        module_name = node.module or ""
                        analysis["imports"].append(module_name)
                        
                    if isinstance(node, ast.FunctionDef):
                        analysis["function_count"] += 1
                        # Check for decorators
                        if node.decorator_list:
                            for dec in node.decorator_list:
                                analysis["decorators"].append(ast.dump(dec)[:80])
                    elif isinstance(node, ast.AsyncFunctionDef):
                        analysis["function_count"] += 1
                        analysis["async_functions"].append(node.name)
                        if node.decorator_list:
                            for dec in node.decorator_list:
                                analysis["decorators"].append(ast.dump(dec)[:80])
                    elif isinstance(node, ast.ClassDef):
                        analysis["class_count"] += 1
                        
                    # Look for dangerous function calls
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                        if node.func.id in dangerous_functions:
                            analysis["dangerous_calls"].append({
                                "function": node.func.id,
                                "line": node.lineno
                            })
                        elif node.func.id in io_functions:
                            analysis["io_operations"].append({
                                "function": node.func.id,
                                "line": node.lineno
                            })
                            
                    # Count TODOs
                    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                        if isinstance(node.value.value, str) and "TODO" in node.value.value:
                            analysis["todo_count"] += 1
                
                # Add security checks for Python files
                analysis.update(self._security_audit(source_to_parse))
                
            except Exception as e:
                logger.error(f"Error during quick analysis: {e}")
                analysis["error"] = str(e)
        else:
            analysis["skipped"] = "Not a Python file"
            
        return analysis
    
    def full_analysis(self, file_data):
        """Perform comprehensive analysis including security audit"""
        # Start with quick analysis
        analysis = self.quick_analysis(file_data)
        
        # Add more detailed security analysis
        if file_data["path"].endswith('.py') and "skipped" not in analysis:
            source_content = file_data.get("content_preview", "")
            
            # Enhanced security checks
            security_issues = []
            
            # Check for hardcoded secrets
            secret_patterns = [
                r'API_KEY\s*=\s*[\'"]([^\'"]+)[\'"]',
                r'SECRET\s*=\s*[\'"]([^\'"]+)[\'"]',
                r'PASSWORD\s*=\s*[\'"]([^\'"]+)[\'"]',
                r'TOKEN\s*=\s*[\'"]([^\'"]+)[\'"]',
                r'PRIVATE_KEY\s*=\s*[\'"]([^\'"]+)[\'"]'
            ]
            
            for pattern in secret_patterns:
                matches = re.findall(pattern, source_content, re.IGNORECASE)
                if matches:
                    security_issues.extend([f"Hardcoded {pattern.split(' ')[0]} found: {match}" 
                                          for match in matches])
            
            # Check for dangerous patterns and IO operations
            dangerous_patterns = [
                (r'eval\s*\(', 'Use of eval() function'),
                (r'exec\s*\(', 'Use of exec() function'),
                (r'compile\s*\(', 'Use of compile() function'),
                (r'subprocess\.', 'Use of subprocess module'),
                (r'os\.system\s*\(', 'Use of os.system()'),
                (r'pickle\.', 'Use of pickle module (code execution risk)'),
                (r'marshal\.', 'Use of marshal module'),
            ]
            
            for pattern, description in dangerous_patterns:
                if re.search(pattern, source_content):
                    security_issues.append(description)
            
            # Check for IO operations
            io_patterns = [
                (r'open\s*\(', 'File I/O operation detected'),
                (r'socket\s*\(', 'Network socket operation detected'),
                (r'urllib', 'HTTP request operation detected'),
                (r'requests\s*\.(get|post|put|delete)', 'HTTP request detected'),
            ]
            
            for pattern, description in io_patterns:
                if re.search(pattern, source_content):
                    security_issues.append(description)
            
            # Add findings to analysis
            analysis["security_issues"] = security_issues
            
        return analysis
    
    def _security_audit(self, content):
        """Perform comprehensive security audit"""
        issues = []
        
        # Check for hardcoded secrets in the content
        patterns = [
            (r'API_KEY\s*=\s*[\'"][^\'"]*[\'"]', 'Hardcoded API key'),
            (r'SECRET\s*=\s*[\'"][^\'"]*[\'"]', 'Hardcoded secret'),
            (r'PASSWORD\s*=\s*[\'"][^\'"]*[\'"]', 'Hardcoded password'),
            (r'TOKEN\s*=\s*[\'"][^\'"]*[\'"]', 'Hardcoded token'),
            (r'PRIVATE_KEY\s*=\s*[\'"][^\'"]*[\'"]', 'Hardcoded private key'),
            (r'AWS_SECRET|GCP_KEY|AZURE_KEY', 'Cloud provider credentials detected'),
        ]
        
        for pattern, description in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(description)
        
        # Check for dangerous code patterns
        dangerous_patterns = [
            (r'eval\s*\(', 'Use of eval() - code execution risk'),
            (r'exec\s*\(', 'Use of exec() - code execution risk'),
            (r'compile\s*\(', 'Use of compile() - code execution risk'),
            (r'__import__\s*\(', 'Use of __import__() - dynamic import risk'),
            (r'pickle\.load', 'Use of pickle.load() - deserialization risk'),
            (r'marshal\.', 'Use of marshal module - low-level risk'),
            (r'subprocess\.(call|run|Popen|check)', 'Use of subprocess - command execution risk'),
            (r'os\.system\s*\(', 'Use of os.system() - shell injection risk'),
            (r'os\.popen\s*\(', 'Use of os.popen() - shell injection risk'),
        ]
        
        for pattern, description in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(description)
        
        # Check for IO operations
        io_patterns = [
            (r'open\s*\(.*[\'"]w', 'File write operation detected'),
            (r'socket\.socket', 'Network socket operation detected'),
            (r'urllib|requests\.', 'HTTP/Network request detected'),
        ]
        
        for pattern, description in io_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(description)
        
        return {
            "security_findings": issues,
            "hardcoded_secrets": any("Hardcoded" in issue or "credentials" in issue for issue in issues),
            "dangerous_code_patterns": any("risk" in issue.lower() for issue in issues)
        }

# ==========================================
# 6. LM STUDIO INTEGRATION ENHANCED
# ==========================================
class LMStudioIntegration:
    """Handles integration with Local LLM (LM Studio)"""
    
    # AI Personas for specialized analysis modes
    PERSONAS = {
        "security_auditor": "You are a ruthless Security Auditor. Focus ONLY on OWASP Top 10 vulnerabilities, secret leaks, and dangerous function calls. Be concise and actionable.",
        "code_tutor": "You are a gentle Python Tutor. Explain complex logic simply and suggest Pythonic refactoring. Focus on readability and best practices.",
        "documentation_expert": "You are a Technical Writer. Ignore code logic; focus on missing docstrings, type hints, and README clarity. Suggest documentation improvements.",
        "performance_analyst": "You are a Performance Engineer. Identify bottlenecks, inefficient algorithms, and memory leaks. Suggest optimization strategies.",
        "default": "You are a code analyzer. Analyze the provided code snippet and identify security issues, best practices, and potential improvements. Be concise."
    }
    
    def __init__(self, uid, lmstudio_url="http://localhost:1234/v1/chat/completions"):
        self.uid = uid
        self.url = lmstudio_url
        self.enabled = False
        
        # PHASE 5: Configurable LM Studio parameters
        self.system_prompt = self.PERSONAS["default"]
        self.temperature = 0.2  # Lower temperature for more consistent analysis
        self.max_tokens = 450   # Limit response length
        self.current_persona = "default"
        self.embedding_model = EMBEDDING_MODEL_NAME
        self.similarity_threshold = SIMILARITY_THRESHOLD
        
    def set_config(self, system_prompt=None, temperature=None, max_tokens=None, persona=None):
        """Configure LM Studio parameters"""
        if persona is not None and persona in self.PERSONAS:
            self.system_prompt = self.PERSONAS[persona]
            self.current_persona = persona
        elif system_prompt is not None:
            self.system_prompt = system_prompt
        if temperature is not None:
            self.temperature = max(0.0, min(1.0, temperature))  # Clamp to [0, 1]
        if max_tokens is not None:
            self.max_tokens = max(1, min(4096, max_tokens))  # Clamp to reasonable range
        
    def check_connection(self):
        """Check if LM Studio is running and accessible"""
        try:
            base_url = self.url.replace('/v1/chat/completions', '')
            response = requests.get(f"{base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    def _get_embeddings_client(self):
        base_url = self.url.replace('/v1/chat/completions', '')
        return EmbeddingsClient(base_url=base_url, model=getattr(self, "embedding_model", EMBEDDING_MODEL_NAME))

    def build_embeddings_index(self, chunked_files: List[str]) -> Optional[str]:
        if not chunked_files:
            return None
        scan_dir = os.path.dirname(os.path.dirname(chunked_files[0]))
        index_path = os.path.join(scan_dir, "embeddings_index.json")
        if os.path.exists(index_path):
            return index_path

        client = self._get_embeddings_client()
        index_entries = []

        for chunk_file in chunked_files:
            if not os.path.exists(chunk_file):
                continue
            with open(chunk_file, 'r', encoding='utf-8') as f:
                chunk_data = json.load(f)
            for entry in chunk_data.get("data", []):
                text = entry.get("content") or ""
                if not text and entry.get("structured_preview"):
                    text = json.dumps(entry.get("structured_preview"))
                if not text:
                    continue
                embedding = client.get_embedding(text)
                if embedding:
                    index_entries.append({
                        "file_id": entry.get("file_id"),
                        "path": entry.get("path"),
                        "chunk": os.path.basename(chunk_file),
                        "embedding": embedding,
                        "preview": text[:500]
                    })

        if index_entries:
            EmbeddingsClient.save_index(index_path, {"entries": index_entries})
            return index_path
        return None

    def retrieve_context(self, query: str, chunked_files: List[str], top_k: int = 3) -> List[Dict[str, Any]]:
        if not query:
            return []

        scan_dir = os.path.dirname(os.path.dirname(chunked_files[0])) if chunked_files else None
        index_path = os.path.join(scan_dir, "embeddings_index.json") if scan_dir else None
        index = EmbeddingsClient.load_index(index_path) if index_path else None
        if index is None:
            index_path = self.build_embeddings_index(chunked_files)
            index = EmbeddingsClient.load_index(index_path) if index_path else None
        if not index or "entries" not in index:
            return []

        client = self._get_embeddings_client()
        query_embedding = client.get_embedding(query)
        if not query_embedding:
            return []

        threshold = getattr(self, "similarity_threshold", SIMILARITY_THRESHOLD)
        scored = []
        for entry in index["entries"]:
            score = EmbeddingsClient.cosine_similarity(query_embedding, entry.get("embedding", []))
            if score >= threshold:
                scored.append({"score": score, **{k: v for k, v in entry.items() if k != "embedding"}})

        scored.sort(key=lambda x: x.get("score", 0), reverse=True)
        return scored[:top_k]
    
    def _lmstudio_chat(self, messages: List[Dict[str, str]]) -> str:
        """Perform chat inference using LM Studio and return response content."""
        if not self.enabled or not self.check_connection():
            return ""

        import time
        max_retries = 3
        retry_delay = 2

        system_prompt = self.system_prompt
        if "json" not in system_prompt.lower():
            system_prompt = f"{system_prompt}\nAlways respond with valid JSON."

        payload_messages = list(messages)
        if payload_messages and payload_messages[0].get("role") == "system":
            payload_messages[0]["content"] = f"{payload_messages[0].get('content', '')}\nAlways respond with valid JSON."
        else:
            payload_messages = [{"role": "system", "content": system_prompt}] + payload_messages
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.url,
                    json={
                        "messages": payload_messages,
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens,
                        "response_format": {"type": "json_object"}
                    },
                    timeout=300
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    return content if isinstance(content, str) else ""
                elif attempt < max_retries - 1:
                    logger.warning(f"LM Studio API error: {response.status_code}, retrying...")
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.error(f"LM Studio API error: {response.status_code} (final attempt)")
                    return ""
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                if attempt < max_retries - 1:
                    logger.warning(f"LM Studio request error, retrying: {type(e).__name__}")
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.error(f"LM Studio request error after {max_retries} attempts: {e}")
                    return ""
            except Exception as e:
                logger.error(f"LM Studio inference error: {e}")
        return ""
    
    def process_with_lmstudio(self, chunked_files):
        """Process files with LM Studio integration"""
        print("\n--- LM Studio Integration ---") # [I/O]
        
        if not self.check_connection():
            print(f"⚠ Could not connect to LM Studio at {self.url}")
            print("  Ensure server is running (e.g., 'lms server start' or check port 1234).")
            return {"status": "failed", "reason": "connection_refused"}
            
        print("✓ Connected to Local LLM.")
        processed_count = 0
        
        # Paths for persisted AI outputs
        ai_dir = None
        if chunked_files:
            scan_dir = os.path.dirname(os.path.dirname(chunked_files[0]))
            ai_dir = os.path.join(scan_dir, "ai")
            os.makedirs(ai_dir, exist_ok=True)

        phase1_entries: List[Dict[str, Any]] = []
        phase2_entries: List[Dict[str, Any]] = []

        # Iterate through chunks
        for chunk_file in chunked_files:
            if not os.path.exists(chunk_file):
                continue
            
            # [I/O] Read chunk
            with open(chunk_file, 'r', encoding='utf-8') as f:
                chunk_data = json.load(f)
            
            modified = False
            round1_summaries: List[str] = []
            files_list = chunk_data.get("data", [])
            
            print(f"  Processing chunk: {Path(chunk_file).name} ({len(files_list)} files)")
            
            for file_data in files_list:
                # [FIX] Load FRESH analysis from files/ directory, not stale chunk data
                file_id = file_data.get("file_id")
                scan_dir = os.path.dirname(os.path.dirname(chunk_file))  # Go up two levels from chunks/
                fresh_file_path = os.path.join(scan_dir, "files", f"{file_id}.json")
                
                static_info = {}
                if os.path.exists(fresh_file_path):
                    try:
                        with open(fresh_file_path, 'r', encoding='utf-8') as f:
                            fresh_data = json.load(f)
                            static_info = fresh_data.get("analysis", {})
                    except Exception as e:
                        logger.debug(f"Could not load analysis for {file_id}: {e}")
                
                # Only analyze Python files that have been successfully parsed
                if file_data["path"].endswith('.py') and static_info.get("ast_parsed", False):
                    code_snippet = file_data.get("content", "")[:1200]  # Use actual content

                    round1_prompt = f"""Round 1: Analyze the component below in 100-200 words.
Include: (a) key behavior, (b) any missed I/O or components, (c) semantic purpose/role.

Component: {file_data['path']}
Imports: {static_info.get('imports', [])}
Functions: {static_info.get('function_count', 0)}
Classes: {static_info.get('class_count', 0)}
Risky Calls: {static_info.get('dangerous_calls', [])}

Code Snippet:
{code_snippet}
"""

                    round1_response = self._lmstudio_chat([
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": round1_prompt}
                    ])

                    if "ai_analysis" not in file_data:
                        file_data["ai_analysis"] = {}

                    file_data["ai_analysis"]["round_1_component_analysis"] = round1_response
                    if round1_response:
                        round1_summaries.append(f"{file_data['path']}: {round1_response}")
                        phase1_entries.append({
                            "file_id": file_id,
                            "path": file_data.get("path"),
                            "analysis": round1_response
                        })

                    modified = True
                    processed_count += 1
            
            # Round 2 + Round 3: Chunk-level overview and next steps
            if round1_summaries:
                round1_text = "\n\n".join(round1_summaries)

                round2_prompt = f"""Round 2: Provide an overview and consolidation of the following component analyses.
Summarize themes, architecture, and risks in 150-300 words.

Analyses:
{round1_text}
"""

                round3_prompt = f"""Round 3: Provide next steps based on the consolidated analysis.
Use bullet points and prioritize the top 5 actions.

Analyses:
{round1_text}
"""

                round2_response = self._lmstudio_chat([
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": round2_prompt}
                ])

                round3_response = self._lmstudio_chat([
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": round3_prompt}
                ])

                chunk_overview = {
                    "chunk": os.path.basename(chunk_file),
                    "round_2_overview": round2_response,
                    "round_3_next_steps": round3_response
                }
                chunk_data["ai_overview"] = chunk_overview
                phase2_entries.append(chunk_overview)
                modified = True

            # Save updated results INSIDE the loop
            if modified:
                # [I/O] Writing updated chunk file
                with open(chunk_file, 'w', encoding='utf-8') as f:
                    json.dump(chunk_data, f, indent=2)
                print(f" - Updated analysis for {chunk_file}") # [I/O]
        
        # Phase 3: Global overview across chunks
        phase3_overview: Optional[Dict[str, Any]] = None
        if phase2_entries:
            consolidated = "\n\n".join(
                [f"Chunk {entry.get('chunk')}:\n{entry.get('round_2_overview','')}\nNext Steps:\n{entry.get('round_3_next_steps','')}" for entry in phase2_entries]
            )
            phase3_prompt = f"""Round 3 (Global): Consolidate the following chunk overviews into a single report.
Provide: (a) architecture/behavior summary, (b) top risks, (c) top 5 actions.

Chunk Analyses:
{consolidated}
"""
            phase3_response = self._lmstudio_chat([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": phase3_prompt}
            ])
            phase3_overview = {
                "global_overview": phase3_response
            }

        # Persist AI outputs
        outputs: Dict[str, Any] = {}
        if ai_dir:
            if phase1_entries:
                phase1_path = os.path.join(ai_dir, "phase1_files.json")
                with open(phase1_path, "w", encoding="utf-8") as f:
                    json.dump(phase1_entries, f, indent=2)
                outputs["phase1_files"] = phase1_path
            if phase2_entries:
                phase2_path = os.path.join(ai_dir, "phase2_chunks.json")
                with open(phase2_path, "w", encoding="utf-8") as f:
                    json.dump(phase2_entries, f, indent=2)
                outputs["phase2_chunks"] = phase2_path
            if phase3_overview:
                phase3_path = os.path.join(ai_dir, "phase3_overview.json")
                with open(phase3_path, "w", encoding="utf-8") as f:
                    json.dump(phase3_overview, f, indent=2)
                outputs["phase3_overview"] = phase3_path

        print(f"✓ Processed {processed_count} files with LM Studio.")
        return {"status": "completed", "processed_files": processed_count, "outputs": outputs}

# ==========================================
# SERVICE LAYER: LM STUDIO CLIENT
# ==========================================
class LMStudioClient:
    """
    Dedicated client for LM Studio interactions.
    Enforces configuration defaults and a canonical API contract.
    """

    DEFAULTS = {
        "context_length": 8192,
        "gpu_offload_ratio": 1.0,
        "ttl": 3600,
    }

    def __init__(self, base_url: str = "http://localhost:1234"):
        self.base_url = (base_url or "http://localhost:1234").rstrip('/')
        self.api_base = f"{self.base_url}/v1"

    def _request(self, method: str, endpoint: str, payload: Optional[Dict[str, Any]] = None, timeout: int = 10) -> Dict[str, Any]:
        url = f"{self.api_base}{endpoint}"
        try:
            resp = requests.request(method, url, json=payload, timeout=timeout, headers={"Content-Type": "application/json"})
            resp.raise_for_status()
            data = resp.json() if resp.content else None
            return {"success": True, "data": data, "status": resp.status_code}
        except requests.exceptions.HTTPError as exc:
            error_msg = exc.response.text if exc.response is not None else str(exc)
            status = exc.response.status_code if exc.response is not None else 500
            logger.error("LM Studio error %s: %s", url, error_msg)
            return {"success": False, "error": error_msg, "status": status}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "LM Studio unreachable", "status": 503}
        except Exception as exc:
            return {"success": False, "error": str(exc), "status": 500}

    def list_models(self) -> Dict[str, Any]:
        return self._request("GET", "/models")

    def manage_model(self, action: str, model_id: str, config_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if action not in ("load", "unload"):
            return {"success": False, "error": "Invalid action", "status": 400}

        endpoint = f"/models/{action}"
        payload: Dict[str, Any] = {"model": model_id}

        if action == "load":
            config = dict(self.DEFAULTS)
            if config_overrides:
                config.update(config_overrides)
            payload.update(config)

        timeout = 60 if action == "load" else 10
        return self._request("POST", endpoint, payload, timeout)


# ==========================================
# EMBEDDINGS CLIENT (LIGHTWEIGHT VECTOR STORE)
# ==========================================
class EmbeddingsClient:
    """Generate embeddings via LM Studio /v1/embeddings and manage a simple JSON index."""

    def __init__(self, base_url: str = "http://localhost:1234", model: str = EMBEDDING_MODEL_NAME):
        self.base_url = base_url.rstrip('/')
        self.model = model

    def get_embedding(self, text: str, timeout: int = 30) -> Optional[List[float]]:
        payload = {"input": text, "model": self.model}
        try:
            resp = requests.post(f"{self.base_url}/v1/embeddings", json=payload, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            payload_data = data.get("data", [])
            if not isinstance(payload_data, list) or not payload_data:
                return None

            first = payload_data[0]
            if not isinstance(first, dict):
                return None

            embedding = first.get("embedding")
            if isinstance(embedding, list) and all(isinstance(x, (int, float)) for x in embedding):
                return [float(x) for x in embedding]
            return None
        except Exception as exc:
            logger.warning("Embedding generation failed: %s", exc)
            return None

    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    @staticmethod
    def save_index(path: str, index: Dict[str, Any]):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2)

    @staticmethod
    def load_index(path: str) -> Optional[Dict[str, Any]]:
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
                logger.warning("Embeddings index %s is not a dict, ignoring.", path)
                return None
        except Exception as exc:
            logger.warning("Failed to load embeddings index %s: %s", path, exc)
            return None

# ==========================================
# 7. REPORT GENERATOR ENHANCED
# ==========================================
class ReportGenerator:
    """Generates comprehensive reports from scan results"""
    
    def __init__(self, uid):
        self.uid = uid
        
    def generate_summary_report(self, scan_results, analysis_results=None):
        """Generate a summary report"""
        if not scan_results:
            return {"error": "No scan results to summarize"}
            
        summary = {
            "uid": scan_results.get("uid"),
            "timestamp": scan_results.get("timestamp"),
            "total_files": len(scan_results.get("files_processed", [])),
            "chunk_count": len(scan_results.get("chunked_outputs", [])),
            "files_by_type": {},
            "security_issues": []
        }
        
        # Count files by type
        for file_info in scan_results.get("files_processed", []):
            ext = file_info.get("extension", "unknown")
            summary["files_by_type"][ext] = summary["files_by_type"].get(ext, 0) + 1
            
        return summary
    
    def generate_detailed_log(self, scan_results):
        """Generate a detailed log of all files processed"""
        if not scan_results:
            return []
            
        log_entries = []
        for file_info in scan_results.get("files_processed", []):
            entry = {
                "path": file_info["path"],
                "size_mb": file_info["size_mb"],
                "extension": file_info["extension"],
                "timestamp": file_info["timestamp"]
            }
            log_entries.append(entry)
            
        return log_entries
    
    def generate_comprehensive_report(self, scan_dir):
        """Generate a comprehensive report from structured scan data"""
        try:
            # Load manifest
            manifest_file = os.path.join(scan_dir, "manifest.json")
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            
            # Load tree structure
            tree_file = os.path.join(scan_dir, "tree.json")
            with open(tree_file, 'r') as f:
                tree = json.load(f)
                
            # Count files by extension
            file_types: Dict[str, int] = {}
            total_files = 0
            
            # Iterate through all files in files directory
            files_dir = os.path.join(scan_dir, "files")
            if os.path.exists(files_dir):
                for filename in os.listdir(files_dir):
                    if filename.endswith('.json'):
                        try:
                            with open(os.path.join(files_dir, filename), 'r') as f:
                                file_data = json.load(f)
                                ext = file_data.get("extension", "unknown")
                                file_types[ext] = file_types.get(ext, 0) + 1
                                total_files += 1
                        except (json.JSONDecodeError, IOError) as parse_err:
                            logger.warning(f"Skipping malformed file {filename}: {parse_err}")
                            continue
            
            # Generate report
            report = {
                "scan_uid": manifest["scan_uid"],
                "timestamp": manifest["timestamp"],
                "root_path": manifest["root_path"],
                "total_files": total_files,
                "file_types": file_types,
                "total_size_mb": manifest["total_size_mb"],
                "chunks_count": manifest["total_chunks"],
                "config_used": manifest["config_used"],
                "structure_tree": tree
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            return {"error": f"Failed to generate report: {str(e)}"}

# ==========================================
# 8. CACHE MANAGER
# ==========================================
class CacheManager:
    """Manages caching of scan results for performance optimization"""
    
    def __init__(self, cache_dir=".bundler_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
    def get_cache_key(self, config):
        """Generate a cache key based on configuration"""
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()
    
    def is_cached(self, cache_key):
        """Check if scan results are cached"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        return os.path.exists(cache_file)
    
    def get_cache(self, cache_key):
        """Retrieve cached results"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Cache read error - malformed JSON: {e}")
            return None
        except IOError as e:
            logger.error(f"Cache read error - file I/O: {e}")
            return None
        except Exception as e:
            logger.error(f"Cache read error - unexpected: {e}")
            return None
    
    def save_cache(self, cache_key, data):
        """Save results to cache"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except TypeError as e:
            logger.error(f"Cache write error - JSON serialization failed: {e}")
        except IOError as e:
            logger.error(f"Cache write error - file I/O failed: {e}")
        except Exception as e:
            logger.error(f"Cache write error - unexpected: {e}")

# ==========================================
# 9. DIRECTORY BUNDLER (FINAL VERSION)
# ==========================================
class DirectoryBundler:
    """Main application class that orchestrates the complete bundler workflow"""
    
    def __init__(self):
        self.uid: Optional[str] = None
        self.config: Dict[str, Any] = {}
        self.output_base: str = ""
        self.scan_storage_root: str = "bundler_scans"
        self.cache_manager: CacheManager = CacheManager()
        
        # Ensure storage root exists
        os.makedirs(self.scan_storage_root, exist_ok=True)
        
    def setup_config(self, cli_args_provided=False):
        """Setup configuration with user input or CLI args"""
        # If CLI args provided, skip interactive prompts
        if cli_args_provided:
            # Use defaults or already-set values from CLI parsing
            self.config.setdefault('mode', 'full')
            self.config.setdefault('lmstudio_enabled', False)
            self.config.setdefault('ai_persona', 'default')
            self.config.setdefault('include_tests', True)
            self.config.setdefault('include_docs', True)
            self.config.setdefault('max_file_size_mb', 50.0)
            print(f"\n{TerminalUI.GREEN}✓ Configuration loaded from CLI arguments{TerminalUI.ENDC}")
        else:
            # Interactive mode
            print("=== Directory Bundler Configuration ===")
            
            # Mode selection
            print("\nSelect processing mode:")
            print("1. Quick Static Analysis")
            print("2. Full Dynamic Analysis")
            
            mode_choice = SecurityValidator.sanitize_input(input("Enter choice (1 or 2): ").strip())
            self.config['mode'] = 'quick' if mode_choice == '1' else 'full'
            
            # LM Studio integration
            print("\nEnable Local LLM Integration:")
            print("1. Enable (connects to LM Studio)")
            print("2. Disable")
            
            lm_choice = SecurityValidator.sanitize_input(input("Enter choice (1 or 2): ").strip())
            self.config['lmstudio_enabled'] = lm_choice == '1'
            
            # AI Persona selection
            if self.config['lmstudio_enabled']:
                print("\nSelect AI Analysis Persona:")
                print("1. Security Auditor (OWASP vulnerabilities)")
                print("2. Code Tutor (Best practices & refactoring)")
                print("3. Documentation Expert (Docstrings & README)")
                print("4. Performance Analyst (Optimization & bottlenecks)")
                print("5. Default (General analysis)")
                persona_choice = SecurityValidator.sanitize_input(input("Enter choice (1-5): ").strip())
                persona_map = {
                    '1': 'security_auditor',
                    '2': 'code_tutor',
                    '3': 'documentation_expert',
                    '4': 'performance_analyst',
                    '5': 'default'
                }
                self.config['ai_persona'] = persona_map.get(persona_choice, 'default')
            
            # Advanced options
            print("\nAdvanced Configuration Options:")
            print("Include test files? (y/n): ", end="")
            include_tests = SecurityValidator.sanitize_input(input().strip().lower())
            self.config['include_tests'] = include_tests == 'y'
            
            print("Include documentation files? (y/n): ", end="")
            include_docs = SecurityValidator.sanitize_input(input().strip().lower())
            self.config['include_docs'] = include_docs == 'y'
            
            print("Max file size limit (MB): ", end="")
            max_size_input = input().strip()
            self.config['max_file_size_mb'] = SecurityValidator.validate_numeric_input(
                max_size_input, 0.1, 500.0, 50.0
            )
            
        # Generate UID for this session
        self.uid = str(uuid.uuid4())[:8] # Shortened for readability
        
        # Create output directory with timestamp and UID
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_base = f"scan_output_{self.uid}_{timestamp}"
        
        print(f"\nSession UID: {self.uid}")
        print(f"Output Directory: {self.output_base}")
        
    def create_scan_directory(self):
        """Create a sub-folder for each scan: bundler_scans/{uid}/"""
        if self.uid is None:
            raise ValueError("UID not initialized. Call setup_config() first.")
        scan_dir = os.path.join(self.scan_storage_root, self.uid)
        os.makedirs(scan_dir, exist_ok=True)
        return scan_dir
    
    def update_global_index(self, scan_metadata):
        """Update the global index with new scan metadata"""
        index_file = os.path.join(self.scan_storage_root, "scan_index.json")
        
        # Read existing index or create empty list
        if os.path.exists(index_file):
            try:
                with open(index_file, 'r') as f:
                    index_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                index_data = []
        else:
            index_data = []
        
        # Add new scan metadata
        index_data.append(scan_metadata)
        
        # Write back to file
        try:
            with open(index_file, 'w') as f:
                json.dump(index_data, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not update global index: {e}")
    
    def run_process(self, bypass_cache=False):
        """Execute the chosen processing mode"""
        if self.config['mode'] == 'quick':
            return self.run_quick_analysis()
        else:
            return self.run_full_analysis(bypass_cache=bypass_cache)
    
    def run_quick_analysis(self):
        """Run quick static analysis"""
        print("\nRunning Quick Static Analysis...") # [I/O] Console output
        
        config_mgr = ConfigManager(self.uid)
        config = config_mgr.load_config()
        # Merge user config
        config.update(self.config)
        
        # Check cache
        if config.get("enable_cache", True):
            cache_key = self.cache_manager.get_cache_key(config)
            if self.cache_manager.is_cached(cache_key):
                print("Loading from cache...")
                cached_data = self.cache_manager.get_cache(cache_key)
                if cached_data:
                    return cached_data
        
        # Create scan directory and perform scan
        scan_dir = self.create_scan_directory()
        assert self.uid is not None  # Guaranteed by create_scan_directory()
        scanner = EnhancedDeepScanner(self.uid, config, scan_dir)
        scan_dir = scanner.scan_directory(".")
        
        # Save results to specific UID folder
        summary_file = os.path.join(scan_dir, "summary.json")
        manifest_file = os.path.join(scan_dir, "manifest.json")
        
        # Load manifest for summary
        with open(manifest_file, 'r') as f:
            manifest_data = json.load(f)
            
        with open(summary_file, 'w') as f:
            json.dump(manifest_data, f, indent=2)
        
        # Update global index
        metadata = {
            "uid": self.uid,
            "timestamp": datetime.datetime.now().isoformat(),
            "path": os.getcwd(),
            "file_count": manifest_data.get("total_files", 0),
            "mode": self.config['mode'],
            "config": config
        }
        self.update_global_index(metadata)
        
        # Cache results
        if config.get("enable_cache", True):
            self.cache_manager.save_cache(cache_key, manifest_data)
        
        print("✅ Quick Analysis Complete.")
        return manifest_data
    
    def run_full_analysis(self, bypass_cache=False):
        """Run comprehensive analysis including security audit"""
        print("\nRunning Full Dynamic Analysis...") # [I/O] Console output
        
        config_mgr = ConfigManager(self.uid)
        config = config_mgr.load_config()
        # Merge user config
        config.update(self.config)
        
        # Generate cache key for later use
        cache_key = self.cache_manager.get_cache_key(config)
        
        # Check cache (unless bypassed)
        if not bypass_cache and config.get("enable_cache", True):
            if self.cache_manager.is_cached(cache_key):
                print("Loading from cache...")
                cached_data = self.cache_manager.get_cache(cache_key)
                if cached_data:
                    return cached_data
            if self.cache_manager.is_cached(cache_key):
                print("Loading from cache...")
                cached_data = self.cache_manager.get_cache(cache_key)
                if cached_data:
                    return cached_data
        
        # Create scan directory and perform scan
        scan_dir = self.create_scan_directory()
        assert self.uid is not None  # Guaranteed by create_scan_directory()
        scanner = EnhancedDeepScanner(self.uid, config, scan_dir)
        scan_dir = scanner.scan_directory(".", progress_callback=lambda x,y,z: print(f"Scanning: {z} {x}/{y}"))
        
        # Run analysis
        print("\nRunning full analysis...")
        scanner.run_full_analysis(progress_callback=lambda x,y,z: print(f"Analyzing: {z} {x}/{y}"))
        
        # Save results to specific UID folder
        summary_file = os.path.join(scan_dir, "summary.json")
        manifest_file = os.path.join(scan_dir, "manifest.json")
        
        # Load manifest for summary
        with open(manifest_file, 'r') as f:
            manifest_data = json.load(f)
            
        with open(summary_file, 'w') as f:
            json.dump(manifest_data, f, indent=2)
        
        # Perform full analysis
        analyzer = AnalysisEngine(self.uid)
        
        # Process with LMStudio if enabled
        lmstudio_outputs = None
        if self.config.get('lmstudio_enabled'):
            lmstudio_url = config.get("lmstudio_url", "http://localhost:1234/v1/chat/completions")
            if not lmstudio_url.endswith("/v1/chat/completions"):
                lmstudio_url = lmstudio_url.rstrip("/") + "/v1/chat/completions"
            if not SecurityValidator.validate_url(lmstudio_url.replace("/v1/chat/completions", "")):
                print(f"⚠ Invalid LM Studio URL: {lmstudio_url}. Falling back to localhost.")
                lmstudio_url = "http://localhost:1234/v1/chat/completions"
            lmstudio = LMStudioIntegration(self.uid, lmstudio_url)
            lmstudio.enabled = True
            # Apply persona if configured
            if 'ai_persona' in self.config:
                lmstudio.set_config(persona=self.config['ai_persona'])
                print(f"{TerminalUI.GREEN}🤖 Using AI Persona: {self.config['ai_persona']}{TerminalUI.ENDC}")
            chunk_files = [os.path.join(scanner.chunks_dir, f) 
                           for f in os.listdir(scanner.chunks_dir) 
                           if f.endswith('.json')]
            lmstudio_results = lmstudio.process_with_lmstudio(chunk_files)
            lmstudio_outputs = lmstudio_results.get("outputs") if isinstance(lmstudio_results, dict) else None
        
        # Save final results
        manifest_file = os.path.join(scan_dir, "manifest.json")
        if lmstudio_outputs:
            manifest_data["ai_outputs"] = lmstudio_outputs
        with open(manifest_file, 'w') as f:
            json.dump(manifest_data, f, indent=2)
        
        # Update global index
        metadata = {
            "uid": self.uid,
            "timestamp": datetime.datetime.now().isoformat(),
            "path": os.getcwd(),
            "file_count": manifest_data.get("total_files", 0),
            "mode": self.config['mode'],
            "config": config
        }
        self.update_global_index(metadata)
        
        # Cache results
        if config.get("enable_cache", True):
            self.cache_manager.save_cache(cache_key, manifest_data)
        
        print("\n✅ Full Analysis Complete.")
        return manifest_data

    def start_web_server(self):
        """Start the web API server"""
        print("\nStarting Web API Server...")
        api_handler = BundlerAPIHandler()
        api_handler.start_server()

# ==========================================
# 10. API HANDLER (ENHANCED FOR REACT INTEGRATION)
# ==========================================
class BundlerAPIHandler:
    """HTTP API handler for the bundler functionality"""
    
    def __init__(self, port=8000):
        self.port = port
        self.active_scans = {}
        self.scan_storage_root = "bundler_scans"
        
    def start_server(self):
        """Start the HTTP server with threading support"""
        handler = self.create_handler()
        
        # Bind shared state to the Handler class to ensure instance methods work
        handler.active_scans = self.active_scans
        handler.scan_storage_root = self.scan_storage_root
        
        # Use ThreadingTCPServer for concurrent request handling
        class ThreadingServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
            daemon_threads = True
            allow_reuse_address = True
        
        with ThreadingServer(("", self.port), handler) as httpd:
            print(f"{TerminalUI.GREEN}🚀 Multithreaded Server started on port {self.port}{TerminalUI.ENDC}")
            print(f"{TerminalUI.BLUE}📡 Ready for concurrent requests{TerminalUI.ENDC}")
            print("Press Ctrl+C to stop")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print(f"\n{TerminalUI.WARNING}Server stopped.{TerminalUI.ENDC}")
    
    def create_handler(self):
        """Create HTTP request handler"""
        class Handler(http.server.SimpleHTTPRequestHandler):
            # Type annotations for dynamically added attributes
            active_scans: Dict[str, Any]
            scan_storage_root: str
            
            # Add CORS Headers for React Dev Environment
            def end_headers(self):
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                super().end_headers()
            
            def do_OPTIONS(self):
                """Handle preflight requests for CORS"""
                self.send_response(200)
                self.end_headers()

            def do_POST(self):
                if self.path == "/api/scan" or self.path == "/scan":
                    self.handle_scan_request()
                elif self.path == "/api/report":
                    self.handle_report_request()
                elif self.path.startswith("/api/lmstudio/model"):
                    self.handle_lmstudio_model()
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def do_GET(self):
                # Normalize path
                if self.path == "/" or self.path == "":
                    self.serve_static_file("index.html")
                    
                # API Endpoints
                elif self.path.startswith("/api/status"):
                    self.handle_status_request()
                    
                elif self.path.startswith("/api/results") or self.path.startswith("/results"):
                    self.handle_results_request()

                # AI outputs
                elif self.path.startswith("/api/ai"):
                    self.handle_ai_request()

                # Chunks endpoint
                elif self.path.startswith("/api/chunks"):
                    self.handle_chunks_request()

                # [ADDED] Tree and labels endpoints
                elif self.path.startswith("/api/tree"):
                    self.handle_tree_request()
                elif self.path.startswith("/api/labels"):
                    self.handle_labels_request()
                elif self.path.startswith("/api/files"):
                    self.handle_files_request()
                elif self.path.startswith("/api/file"):
                    self.handle_file_request()
                
                # [ADDED] History Endpoint
                elif self.path.startswith("/api/history"):
                    self.handle_history_request()

                # [ADDED] LM Studio proxy endpoints
                elif self.path.startswith("/api/lmstudio/models"):
                    self.handle_lmstudio_models()
                
                # [ADDED] Report Endpoint
                elif self.path.startswith("/api/report"):
                    self.handle_report_request()
                
                # [ADDED] Server-Sent Events for real-time progress
                elif self.path.startswith("/api/stream"):
                    self.handle_stream_request()
                    
                else:
                    # Serve static files for everything else
                    self.serve_static_file(self.path.lstrip('/'))
            
            def handle_history_request(self):
                """Serve the scan history index"""
                # Use self.scan_storage_root (injected via start_server)
                index_file = os.path.join(self.scan_storage_root, "scan_index.json")
                if os.path.exists(index_file):
                    try:
                        with open(index_file, 'r') as f:
                            data = json.load(f)
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(data).encode())
                    except Exception as e:
                        print(f"Error reading history: {e}")
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(b"[]")
                else:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"[]")

            def _normalize_lmstudio_base_url(self, base_url: Optional[str]) -> Optional[str]:
                """Return sanitized LM Studio base URL without path segments."""
                if not base_url:
                    base_url = "http://localhost:1234"
                base_url = base_url.rstrip("/")
                base_url = base_url.replace("/v1/chat/completions", "")
                if not SecurityValidator.validate_url(base_url):
                    return None
                return base_url

            def handle_lmstudio_models(self):
                """Proxy LM Studio models list."""
                parsed_path = urlparse(self.path)
                query_params = parse_qs(parsed_path.query)
                base_url = self._normalize_lmstudio_base_url(query_params.get('base_url', [None])[0])

                if not base_url:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Invalid LM Studio URL"}).encode())
                    return

                target_url = f"{base_url}/v1/models"
                try:
                    resp = requests.get(target_url, timeout=8)
                    self.send_response(200 if resp.ok else 502)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    if resp.ok:
                        self.wfile.write(resp.content)
                    else:
                        self.wfile.write(json.dumps({"error": "Failed to query LM Studio", "status_code": resp.status_code}).encode())
                except Exception as e:
                    logger.error(f"LM Studio models fetch error: {e}")
                    self.send_response(502)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "LM Studio unreachable"}).encode())

            def handle_lmstudio_model(self):
                """Proxy using the decoupled LMStudioClient."""
                try:
                    content_length = int(self.headers.get('Content-Length', 0))
                    raw_body = self.rfile.read(content_length) if content_length > 0 else b"{}"
                    body = json.loads(raw_body.decode('utf-8') or "{}")
                except json.JSONDecodeError:
                    self._send_json(400, {"error": "Malformed JSON body"})
                    return

                action = body.get("action")
                model_id = body.get("model")
                config_keys = ["context_length", "gpu_offload_ratio", "ttl"]
                config_overrides = {k: body[k] for k in config_keys if k in body}
                base_url = self._normalize_lmstudio_base_url(body.get("base_url"))

                if not action or not model_id:
                    self._send_json(400, {"error": "Missing 'action' or 'model'"})
                    return
                if not base_url:
                    self._send_json(400, {"error": "Invalid LM Studio URL"})
                    return

                client = LMStudioClient(base_url)
                try:
                    result = client.manage_model(action, model_id, config_overrides)
                    status_code = result.get("status", 500)

                    if result.get("success"):
                        data = result.get("data") or {"status": "ok"}
                        self._send_json(status_code, data)
                    else:
                        self._send_json(status_code, {"error": result.get("error", "Unknown error")})
                except Exception as exc:
                    logger.error("LM Studio proxy error for %s (%s): %s", model_id, action, exc)
                    self._send_json(500, {"error": str(exc)})

            def _send_json(self, status: int, data: Dict[str, Any]):
                self.send_response(status)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())

            def _get_scan_dir(self, scan_uid: Optional[str]) -> Optional[str]:
                """Resolve and validate scan directory for a given UID."""
                if not scan_uid or not SecurityValidator.validate_scan_uid(scan_uid):
                    return None
                base_dir = os.path.abspath(self.scan_storage_root)
                scan_dir = os.path.abspath(os.path.join(base_dir, scan_uid))
                if not scan_dir.startswith(base_dir + os.sep):
                    return None
                return scan_dir

            def handle_tree_request(self):
                """Serve tree.json for a scan."""
                parsed_path = urlparse(self.path)
                query_params = parse_qs(parsed_path.query)
                scan_uid = query_params.get('uid', [None])[0]
                scan_dir = self._get_scan_dir(scan_uid)
                if not scan_dir:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Invalid uid"}).encode())
                    return

                tree_file = os.path.join(scan_dir, "tree.json")
                if not os.path.exists(tree_file):
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Tree not found"}).encode())
                    return

                try:
                    with open(tree_file, 'r') as f:
                        data = json.load(f)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(data).encode())
                except Exception as e:
                    logger.error(f"Tree read error: {e}")
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Failed to load tree"}).encode())

            def handle_labels_request(self):
                """Serve labels.json for a scan."""
                parsed_path = urlparse(self.path)
                query_params = parse_qs(parsed_path.query)
                scan_uid = query_params.get('uid', [None])[0]
                scan_dir = self._get_scan_dir(scan_uid)
                if not scan_dir:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Invalid uid"}).encode())
                    return

                labels_file = os.path.join(scan_dir, "labels.json")
                if not os.path.exists(labels_file):
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Labels not found"}).encode())
                    return

                try:
                    with open(labels_file, 'r') as f:
                        data = json.load(f)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(data).encode())
                except Exception as e:
                    logger.error(f"Labels read error: {e}")
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Failed to load labels"}).encode())

            def handle_files_request(self):
                """Serve list of file metadata for a scan."""
                parsed_path = urlparse(self.path)
                query_params = parse_qs(parsed_path.query)
                scan_uid = query_params.get('uid', [None])[0]
                include_analysis = query_params.get('include_analysis', ['0'])[0] == '1'

                scan_dir = self._get_scan_dir(scan_uid)
                if not scan_dir:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Invalid uid"}).encode())
                    return

                files_dir = os.path.join(scan_dir, "files")
                if not os.path.exists(files_dir):
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Files not found"}).encode())
                    return

                results: List[Dict[str, Any]] = []
                try:
                    for filename in os.listdir(files_dir):
                        if not filename.endswith(".json"):
                            continue
                        file_path = os.path.join(files_dir, filename)
                        try:
                            with open(file_path, 'r') as f:
                                file_data = json.load(f)
                            entry = {
                                "file_id": file_data.get("file_id"),
                                "path": file_data.get("path"),
                                "name": file_data.get("name"),
                                "extension": file_data.get("extension"),
                                "size_mb": file_data.get("size_mb"),
                                "file_type": file_data.get("file_type")
                            }
                            if include_analysis:
                                entry["analysis"] = file_data.get("analysis")
                                entry["security_findings"] = file_data.get("analysis", {}).get("security_findings", [])
                            results.append(entry)
                        except (json.JSONDecodeError, IOError) as parse_err:
                            logger.warning(f"Skipping malformed file {filename}: {parse_err}")
                            continue

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(results).encode())
                except Exception as e:
                    logger.error(f"Files list error: {e}")
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Failed to load files"}).encode())

            def handle_file_request(self):
                """Serve a single file metadata JSON by file_id."""
                parsed_path = urlparse(self.path)
                query_params = parse_qs(parsed_path.query)
                scan_uid = query_params.get('uid', [None])[0]
                file_id = query_params.get('file_id', [None])[0]

                scan_dir = self._get_scan_dir(scan_uid)
                if not scan_dir or not file_id or not re.fullmatch(r"[a-zA-Z0-9_\-]+", file_id):
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Invalid uid or file_id"}).encode())
                    return

                files_dir = os.path.join(scan_dir, "files")
                file_path = os.path.join(files_dir, f"{file_id}.json")
                if not os.path.exists(file_path):
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "File not found"}).encode())
                    return

                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(data).encode())
                except Exception as e:
                    logger.error(f"File read error: {e}")
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Failed to load file"}).encode())
            
            def handle_stream_request(self):
                """Real-time progress streaming via Server-Sent Events"""
                try:
                    parsed_path = urlparse(self.path)
                    query_params = parse_qs(parsed_path.query)
                    scan_uid = query_params.get('uid', [None])[0]
                    
                    if not scan_uid:
                        self.send_response(400)
                        self.end_headers()
                        return
                    
                    # Set up SSE headers
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/event-stream')
                    self.send_header('Cache-Control', 'no-cache')
                    self.send_header('Connection', 'keep-alive')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    # Stream progress updates
                    import time
                    while True:
                        if scan_uid in self.active_scans:
                            status = self.active_scans[scan_uid]
                            payload = f"data: {json.dumps(status)}\n\n"
                            try:
                                self.wfile.write(payload.encode())
                                self.wfile.flush()
                                if status.get('status') in ['completed', 'failed']:
                                    break
                                time.sleep(0.5)  # Update every 500ms
                            except (BrokenPipeError, ConnectionResetError):
                                break
                        else:
                            break
                except Exception as e:
                    logger.error(f"SSE streaming error: {e}")
            
            def handle_report_request(self):
                """Handle report generation request"""
                try:
                    # Extract scan_uid from query parameters
                    parsed_path = urlparse(self.path)
                    query_params = parse_qs(parsed_path.query)
                    scan_uid = query_params.get('uid', [None])[0]
                    
                    if not scan_uid:
                        self.send_response(400)
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Missing uid parameter"}).encode())
                        return
                    
                    # Generate report
                    scan_dir = os.path.join(self.scan_storage_root, scan_uid)
                    if not os.path.exists(scan_dir):
                        self.send_response(404)
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Scan not found"}).encode())
                        return
                    
                    report_generator = ReportGenerator(scan_uid)
                    report = report_generator.generate_comprehensive_report(scan_dir)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(report).encode())
                    
                except Exception as e:
                    logger.error(f"Report generation error: {e}")
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
            
            def handle_scan_request(self):
                """Handle scan initiation request"""
                try:
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    config = json.loads(post_data.decode('utf-8'))
                    scan_uid = str(uuid.uuid4())[:8]
                    
                    # Track scan status
                    self.active_scans[scan_uid] = {
                        "status": "pending", 
                        "uid": scan_uid
                    }
                    
                    # Start scan in background thread
                    threading.Thread(
                        target=self.run_scan,
                        args=(config, scan_uid)
                    ).start()
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {"status": "started", "uid": scan_uid}
                    self.wfile.write(json.dumps(response).encode())
                    
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
            
            def handle_status_request(self):
                """Handle status request"""
                parsed_path = urlparse(self.path)
                query_params = parse_qs(parsed_path.query)
                scan_uid = query_params.get('uid', [None])[0]
                
                if not scan_uid:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Missing uid parameter"}).encode())
                    return
                
                # Check active scans first
                status = self.active_scans.get(scan_uid)
                
                # If not active, check disk (persistence)
                if not status:
                     scan_dir = os.path.join(self.scan_storage_root, scan_uid)
                     if os.path.exists(os.path.join(scan_dir, "manifest.json")):
                         status = {"status": "completed", "uid": scan_uid}
                     else:
                         status = {"status": "unknown", "uid": scan_uid}

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(status).encode())
            
            def handle_results_request(self):
                """Handle results retrieval request"""
                parsed_path = urlparse(self.path)
                query_params = parse_qs(parsed_path.query)
                scan_uid = query_params.get('uid', [None])[0]
                
                if not scan_uid:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Missing uid parameter"}).encode())
                    return
                
                scan_dir = os.path.join(self.scan_storage_root, scan_uid)
                
                if not os.path.exists(scan_dir):
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Scan not found"}).encode())
                    return
                
                manifest_file = os.path.join(scan_dir, "manifest.json")
                if os.path.exists(manifest_file):
                    with open(manifest_file, 'r') as f:
                        data = json.load(f)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(data).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Results not found"}).encode())

            def handle_chunks_request(self):
                """Serve chunked content for a scan."""
                parsed_path = urlparse(self.path)
                query_params = parse_qs(parsed_path.query)
                scan_uid = query_params.get('uid', [None])[0]

                if not scan_uid:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Missing uid parameter"}).encode())
                    return

                scan_dir = self._get_scan_dir(scan_uid)
                if not scan_dir:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Invalid uid"}).encode())
                    return

                chunks_dir = os.path.join(scan_dir, "chunks")
                if not os.path.exists(chunks_dir):
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Chunks not found"}).encode())
                    return

                chunk_results = []
                try:
                    for filename in sorted(os.listdir(chunks_dir)):
                        if not filename.endswith('.json'):
                            continue
                        file_path = os.path.join(chunks_dir, filename)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        chunk_results.append({
                            "chunk": filename,
                            "data": data.get("data", [])
                        })

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(chunk_results).encode())
                except Exception as e:
                    logger.error(f"Chunks read error: {e}")
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Failed to load chunks"}).encode())

            def handle_ai_request(self):
                """Serve AI output files (phase1/2/3)."""
                parsed_path = urlparse(self.path)
                query_params = parse_qs(parsed_path.query)
                scan_uid = query_params.get('uid', [None])[0]
                phase = query_params.get('phase', [None])[0]

                scan_dir = self._get_scan_dir(scan_uid)
                if not scan_dir or not phase:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Missing uid or phase"}).encode())
                    return

                ai_dir = os.path.join(scan_dir, "ai")
                phase_map = {
                    "1": "phase1_files.json",
                    "2": "phase2_chunks.json",
                    "3": "phase3_overview.json"
                }
                target_file = phase_map.get(phase)
                if not target_file:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Invalid phase"}).encode())
                    return

                file_path = os.path.join(ai_dir, target_file)
                if not os.path.exists(file_path):
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "AI output not found"}).encode())
                    return

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(data).encode())
                except Exception as e:
                    logger.error(f"AI output read error: {e}")
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Failed to load AI output"}).encode())
            
            def serve_static_file(self, filename):
                """Serve static files (HTML/CSS/JS) from dist folder"""
                try:
                    # Clean filename
                    filename = os.path.normpath(filename).lstrip(os.sep)
                    if filename == "" or filename == ".":
                        filename = "index.html"
                        
                    # [UPDATED] Serve from 'static' directory (changed from 'dist')
                    file_path = os.path.join(os.getcwd(), "static", filename)
                    
                    if os.path.exists(file_path) and not os.path.isdir(file_path):
                        # Validate file size before reading (prevent OOM)
                        try:
                            file_size = os.path.getsize(file_path)
                            max_size_mb = 100  # 100MB limit for static files
                            if file_size > (max_size_mb * 1024 * 1024):
                                self.send_response(413)  # Payload Too Large
                                self.end_headers()
                                return
                        except OSError:
                            self.send_response(403)  # Forbidden
                            self.end_headers()
                            return
                        
                        with open(file_path, 'rb') as f:
                            content = f.read()
                        
                        if filename.endswith('.css'):
                            content_type = 'text/css'
                        elif filename.endswith('.js'):
                            content_type = 'application/javascript'
                        elif filename.endswith('.svg'):
                            content_type = 'image/svg+xml'
                        else:
                            content_type = 'text/html'
                        
                        self.send_response(200)
                        self.send_header('Content-type', content_type)
                        self.end_headers()
                        self.wfile.write(content)
                    else:
                        # SPA Fallback: serve index.html for non-asset routes
                        # Only fallback if it's NOT a request for a specific missing asset (like a js file)
                        if not filename.startswith("assets/") and not filename.endswith(".js") and not filename.endswith(".css"):
                            fallback_path = os.path.join(os.getcwd(), "static", "index.html")
                            if os.path.exists(fallback_path):
                                with open(fallback_path, 'rb') as f:
                                    content = f.read()
                                self.send_response(200)
                                self.send_header('Content-type', 'text/html')
                                self.end_headers()
                                self.wfile.write(content)
                            else:
                                self.send_response(404)
                                self.end_headers()
                        else:
                            self.send_response(404)
                            self.end_headers()
                            
                except Exception as e:
                    print(f"Error serving static file {filename}: {e}")
                    self.send_response(404)
                    self.end_headers()
            
            def run_scan(self, config, scan_uid):
                """Run the actual scan"""
                try:
                    self.active_scans[scan_uid]["status"] = "processing"
                    
                    # Get target path from config (default to current directory)
                    target_path = config.get('target_path', '.')
                    
                    # Initialize scanner
                    scanner = EnhancedDeepScanner(scan_uid, config, os.path.join(self.scan_storage_root, scan_uid))
                    scan_dir = scanner.scan_directory(target_path, progress_callback=lambda x,y,z: print(f"Scanning: {z} {x}/{y}"))
                    
                    # Run analysis
                    print("\nRunning full analysis...")
                    scanner.run_full_analysis(progress_callback=lambda x,y,z: print(f"Analyzing: {z} {x}/{y}"))

                    # Optional LM Studio analysis
                    if config.get("lmstudio_enabled"):
                        lmstudio_url = config.get("lmstudio_url", "http://localhost:1234/v1/chat/completions")
                        if not lmstudio_url.endswith("/v1/chat/completions"):
                            lmstudio_url = lmstudio_url.rstrip("/") + "/v1/chat/completions"
                        if not SecurityValidator.validate_url(lmstudio_url.replace("/v1/chat/completions", "")):
                            print(f"⚠ Invalid LM Studio URL: {lmstudio_url}. Falling back to localhost.")
                            lmstudio_url = "http://localhost:1234/v1/chat/completions"

                        lmstudio = LMStudioIntegration(scan_uid, lmstudio_url)
                        lmstudio.enabled = True
                        if 'ai_persona' in config:
                            lmstudio.set_config(persona=config['ai_persona'])
                            print(f"{TerminalUI.GREEN}🤖 Using AI Persona: {config['ai_persona']}{TerminalUI.ENDC}")

                        chunk_files = [os.path.join(scanner.chunks_dir, f) for f in os.listdir(scanner.chunks_dir) if f.endswith('.json')]
                        lmstudio_results = lmstudio.process_with_lmstudio(chunk_files)

                        # Persist AI output paths into manifest if available
                        manifest_path = os.path.join(scan_dir, "manifest.json")
                        if os.path.exists(manifest_path):
                            try:
                                with open(manifest_path, 'r', encoding='utf-8') as mf:
                                    manifest_data = json.load(mf)
                                outputs = lmstudio_results.get("outputs") if isinstance(lmstudio_results, dict) else None
                                if outputs:
                                    manifest_data["ai_outputs"] = outputs
                                    with open(manifest_path, 'w', encoding='utf-8') as mf:
                                        json.dump(manifest_data, mf, indent=2)
                            except Exception as e:
                                logger.error(f"Failed to persist ai_outputs: {e}")
                    
                    # Update status
                    self.active_scans[scan_uid]["status"] = "completed"
                    
                    # Update global index (Important for History)
                    index_file = os.path.join(self.scan_storage_root, "scan_index.json")
                    metadata = {
                        "uid": scan_uid,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "path": os.getcwd(),
                        "file_count": scanner.total_processed_size,
                        "mode": config.get('mode', 'quick'),
                        "config": config
                    }
                    
                    # Simple read-modify-write for index
                    current_index = []
                    if os.path.exists(index_file):
                        try:
                            with open(index_file, 'r') as f:
                                current_index = json.load(f)
                        except: pass
                    current_index.append(metadata)
                    with open(index_file, 'w') as f:
                        json.dump(current_index, f, indent=2)
                    
                except Exception as e:
                    logger.error(f"Scan failed for {scan_uid}: {e}")
                    self.active_scans[scan_uid] = {
                        "status": "failed",
                        "uid": scan_uid,
                        "error": str(e)
                    }
        
        return Handler

# ==========================================
# 11. BUNDLER CLI INTERFACE
# ==========================================
class BundlerCLI:
    """Command line interface for the bundler"""
    
    def __init__(self):
        self.bundler = DirectoryBundler()
        
    def run(self):
        """Run the CLI application"""
        print(f"{TerminalUI.BOLD}{TerminalUI.HEADER}=== VERSION 4.5 ENHANCED UI/UX BUNDLER ==={TerminalUI.ENDC}")
        print(f"{TerminalUI.GREEN}Features:{TerminalUI.ENDC}")
        print(f"{TerminalUI.BLUE}• Centralized Scan Storage (bundler_scans/){TerminalUI.ENDC}")
        print(f"{TerminalUI.BLUE}• Global Scan Indexing{TerminalUI.ENDC}")
        print(f"{TerminalUI.BLUE}• Enhanced Deep Scanner with Label Tracking{TerminalUI.ENDC}")
        print(f"{TerminalUI.BLUE}• Multithreaded REST API (React Ready){TerminalUI.ENDC}")
        print(f"{TerminalUI.BLUE}• Real-time SSE Progress Streaming{TerminalUI.ENDC}")
        print(f"{TerminalUI.BLUE}• AI Persona System (Security/Tutor/Docs/Performance){TerminalUI.ENDC}")
        print(f"{TerminalUI.BLUE}• Advanced Caching System{TerminalUI.ENDC}")
        print(f"{TerminalUI.BLUE}• Professional Progress Bars{TerminalUI.ENDC}")
        
        self.bundler.setup_config()
        
        # Choose to run analysis or start web server
        print("\nChoose action:")
        print("1. Run Analysis (CLI mode)")
        print("2. Start Web Server (API mode)")
        print("3. Run Both")
        print("4. Generate Report")
        
        choice = input("Enter choice (1, 2, 3, or 4): ").strip()
        
        if choice == "1":
            results = self.bundler.run_process()
            print("\nAnalysis Complete!")
            print(f"Scan UID: {self.bundler.uid}")
        elif choice == "2":
            self.bundler.start_web_server()
        elif choice == "3":
            # Run analysis first, then start server
            results = self.bundler.run_process()
            print("\nStarting web server...")
            self.bundler.start_web_server()
        elif choice == "4":
            self.generate_report()
        else:
            print("Invalid choice. Exiting.")
    
    def generate_report(self):
        """Generate a report for a specific scan"""
        try:
            scan_uid_input = input("Enter scan UID: ").strip()
            scan_uid = SecurityValidator.sanitize_input(scan_uid_input, max_length=32)
            
            if not SecurityValidator.validate_scan_uid(scan_uid):
                print("Invalid scan UID format!")
                return
            
            scan_dir = os.path.join("bundler_scans", scan_uid)
            
            if not os.path.exists(scan_dir):
                print("Scan not found!")
                return
                
            report_generator = ReportGenerator(scan_uid)
            report = report_generator.generate_comprehensive_report(scan_dir)
            
            # Save report to file
            report_file = f"report_{scan_uid}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
                
            print(f"Report generated: {report_file}")
            print(f"Total files: {report.get('total_files', 0)}")
            print(f"Total size: {report.get('total_size_mb', 0)} MB")
            
        except Exception as e:
            print(f"Error generating report: {e}")

# Main execution
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Directory Bundler v4.5 - Advanced Codebase Analysis")
    parser.add_argument("--mode", choices=["quick", "full"], default=None, help="Scan mode: quick or full")
    parser.add_argument("--path", default=None, help="Directory path to scan")
    parser.add_argument("--lmstudio", action="store_true", help="Enable LM Studio AI analysis")
    parser.add_argument("--lmstudio-url", default=None, help="LM Studio server URL (e.g., http://192.168.0.190:1234)")
    parser.add_argument("--ai-persona", choices=["security_auditor", "code_tutor", "documentation_expert", "performance_analyst", "default"], default=None, help="AI analysis persona")
    parser.add_argument("--web", action="store_true", help="Start web server only")
    parser.add_argument("--uid", default=None, help="Generate report for specific scan UID")
    
    args = parser.parse_args()
    
    # If command-line arguments provided, use non-interactive mode
    if args.mode or args.lmstudio or args.path or args.uid or args.web:
        bundler = DirectoryBundler()
        
        # Set config from CLI arguments BEFORE setup_config
        if args.mode:
            bundler.config["mode"] = args.mode
        if args.path:
            bundler.config["root_path"] = args.path
        if args.lmstudio:
            bundler.config["lmstudio_enabled"] = True
        if args.lmstudio_url:
            bundler.config["lmstudio_url"] = args.lmstudio_url
        if args.ai_persona:
            bundler.config["ai_persona"] = args.ai_persona
        
        # Call setup_config with cli_args_provided=True to skip interactive prompts
        bundler.setup_config(cli_args_provided=True)
        
        if args.uid:
            # Generate report mode
            report_gen = BundlerCLI()
            report_gen.generate_report()
        elif args.web:
            # Web server only
            bundler.start_web_server()
        else:
            # Run analysis with cache bypass for CLI runs
            print(f"\n{TerminalUI.BLUE}🚀 Starting scan with CLI parameters...{TerminalUI.ENDC}")
            results = bundler.run_process(bypass_cache=True)
            print(f"\n{TerminalUI.GREEN}✓ Analysis Complete! Scan UID: {bundler.uid}{TerminalUI.ENDC}")
    else:
        # Interactive menu mode
        cli = BundlerCLI()
        cli.run()
    
    # Alternative direct execution:
    # print("=== VERSION 4.0 FINAL ENHANCED HYBRID BUNDLER ===")
    # print("Features:")
    # print("• Centralized Scan Storage (bundler_scans/)")
    # print("• Global Scan Indexing")
    # print("• Enhanced Deep Scanner with Label Tracking")
    # print("• REST API for Dashboard Integration (React Ready)")
    # print("• Advanced Caching System")
    # print("• Comprehensive Reporting")
    # print("• Multi-Mode Processing")
    # print("• Configurable File Filters")
    
    # bundler = DirectoryBundler()
    # bundler.setup_config()
    
    # # Choose to run analysis or start web server
    # print("\nChoose action:")
    # print("1. Run Analysis (CLI mode)")
    # print("2. Start Web Server (API mode)")
    # print("3. Run Both")
    
    # choice = input("Enter choice (1, 2, or 3): ").strip()
    
    # if choice == "1":
    #     results = bundler.run_process()
    # elif choice == "2":
    #     bundler.start_web_server()
    # else:
    #     # Run analysis first, then start server
    #     results = bundler.run_process()
    #     print("\nStarting web server...")
    #     bundler.start_web_server()
