import importlib
import logging
from pathlib import Path
from typing import Any, Dict, List, cast
from config.settings import settings  # type: ignore[import]
from utils import ocr_service  # type: ignore[import]

fitz = cast(Any, importlib.import_module("fitz"))

logger = logging.getLogger(__name__)

class PDFProcessor:
    """
    Specialized processor for PDF documents with OCR capabilities.
    """
    def __init__(self):
        self.settings = settings

    def process_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Extracts text from PDF page-by-page, applying OCR if text density is low.
        """
        documents = []
        ocr_available = True  # stop retrying if deps are missing
        try:
            doc = fitz.open(file_path)
            for page_num, page in enumerate(doc):
                raw_text = page.get_text()

                # Decision Gate: Check for Scanned Pages
                if len(raw_text.strip()) < self.settings.OCR_TEXT_DENSITY_THRESHOLD and ocr_available:
                    logger.warning(f"Low text density on page {page_num + 1} of {file_path.name}. Checking OCR...")
                    try:
                        image = ocr_service.convert_page_to_image(str(file_path), page_num + 1)
                        if image:
                            ocr_text = ocr_service.extract_text_from_image(image)
                            if len(ocr_text.strip()) > len(raw_text.strip()):
                                raw_text = ocr_text
                                logger.info(f"OCR improved text yield for page {page_num + 1}.")
                    except EnvironmentError as env_err:
                        logger.warning(f"OCR disabled for {file_path.name}: {env_err}")
                        ocr_available = False
                    except Exception as ocr_e:
                        logger.error(f"OCR failed for page {page_num + 1}: {ocr_e}")

                # Chunking
                if raw_text.strip():
                    page_docs = self._chunk_text(raw_text, str(file_path), file_path.name, page_num + 1)
                    documents.extend(page_docs)
            
            doc.close()
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}")
            
        return documents

    def _chunk_text(self, text: str, file_path: str, file_name: str, page_num: int) -> List[Dict[str, Any]]:
        """Helper to split text into chunks."""
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
                    "page_number": page_num,
                    "chunk_index": chunk_idx,
                    "file_type": "pdf"
                }
            })
            
            start += (chunk_size - overlap)
            chunk_idx += 1
            
        return chunks