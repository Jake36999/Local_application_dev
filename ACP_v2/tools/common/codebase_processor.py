import logging
from pathlib import Path
from typing import List, Dict, Any
from config.settings import settings

# Module-level annotation
documents: List[Any] = []

logger = logging.getLogger(__name__)

class CodebaseProcessor:
    """
    Handles processing of text-based files (Python, JSON, Markdown, etc.).
    """
    def __init__(self):
        self.settings = settings

    from config.settings import settings
    def process_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Reads text/code files directly and chunks them."""
        documents: List[Any] = []
        try:
            # Use errors='ignore' to prevent crashing on non-UTF-8 binary artifacts
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                raw_text = f.read()
            
            if raw_text.strip():
                return self._chunk_text(raw_text, str(file_path), file_path.name)
        except Exception as e:
            logger.error(f"Error processing text file {file_path.name}: {e}")
        return documents

    def _chunk_text(self, text: str, file_path: str, file_name: str) -> List[Dict[str, Any]]:
        """Splits text into sliding window chunks."""
        chunk_size = self.settings.CHUNK_SIZE
        overlap = self.settings.CHUNK_OVERLAP
        chunks = []
        
        text_len = len(text)
        start = 0
        chunk_idx = 0
        
        while start < text_len:
            end = min(start + chunk_size, text_len)
            chunk_content = text[start:end]
            
            chunks.append({
                "content": chunk_content,
                "metadata": {
                    "file_path": file_path,
                    "file_name": file_name,
                    "page_number": 0, # Not applicable for flat text files
                    "chunk_index": chunk_idx,
                    "file_type": "codebase"
                }
            })
            
            start += (chunk_size - overlap)
            chunk_idx += 1
            
        return chunks