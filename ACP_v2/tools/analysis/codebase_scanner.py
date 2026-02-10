import os
from pathlib import Path
from typing import List, Set

class CodebaseScanner:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        
        # EXCLUSION LIST: Folders to strictly ignore
        self.ignore_dirs = {
            '.git', '__pycache__', 'venv', 'node_modules', 
            '.vscode', 'dist', 'coverage', 'chroma_db',
            '.mypy_cache', '.pytest_cache', 'typings', 'site-packages',
            '__pypackages__'
        }
        
        # EXCLUSION LIST: Files to ignore
        self.ignore_files = {
            '.DS_Store', 'package-lock.json', 'yarn.lock', 
            'poetry.lock', 'simulation_ledger.csv', '.env'
        }

    def get_directory_tree(self) -> str:
        """Generates a clean visual tree structure of the project."""
        tree_lines = [f"Project Root: {self.root_dir.name}"]
        
        for root, dirs, files in os.walk(self.root_dir):
            # Modify dirs in-place to skip ignored folders
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            level = root.replace(str(self.root_dir), '').count(os.sep)
            indent = ' ' * 4 * (level)
            tree_lines.append(f"{indent}{os.path.basename(root)}/")
            
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                if f not in self.ignore_files and not f.endswith('.pyc'):
                    tree_lines.append(f"{subindent}{f}")
                    
        return "\n".join(tree_lines)

    def get_critical_files_content(self) -> str:
        """Reads key configuration and architecture files for context."""
        # Add files here that you want the AI to always know about
        critical_paths = [
            "config/settings.py",
            "main_platform.py",
            "aletheia_mcp.py",
            "system_manifest.py",
            "tools/ingest/ingest_manager.py" 
        ]
        
        content_summary = "\n\n--- CRITICAL SYSTEM FILES ---\n"
        for rel_path in critical_paths:
            full_path = self.root_dir / rel_path
            if full_path.exists():
                content_summary += f"\nFile: {rel_path}\n"
                content_summary += "-" * 40 + "\n"
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content_summary += f.read()
                except Exception as e:
                    content_summary += f"[Error reading file: {e}]"
                content_summary += "\n" + "-" * 40 + "\n"
        return content_summary

    def generate_system_snapshot(self) -> str:
        """Combines tree and content into a prompt-ready snapshot."""
        return (
            "--- ALETHEIA SYSTEM SNAPSHOT ---\n"
            f"{self.get_directory_tree()}\n"
            f"{self.get_critical_files_content()}"
        )

if __name__ == "__main__":
    scanner = CodebaseScanner()
    print(scanner.get_directory_tree())