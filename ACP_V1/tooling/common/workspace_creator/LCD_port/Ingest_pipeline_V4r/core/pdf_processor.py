import importlib
import logging
from pathlib import Path
from typing import Any, Dict, List, cast

fitz = cast(Any, importlib.import_module("fitz"))

from config.settings import settings
from utils import ocr_service

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Extract text from PDFs with an OCR fallback and rich chunk metadata."""

    def __init__(self) -> None:
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        self.density_threshold = settings.OCR_TEXT_DENSITY_THRESHOLD

    def process_file(self, file_path: Path) -> List[Dict[str, Any]]:
        documents: List[Dict[str, Any]] = []
        ocr_available = True
        doc_chunk_counter = 0
        try:
            doc = fitz.open(file_path)
        except Exception as exc:  # pylint: disable=broad-except
            logger.error(f"Unable to open PDF {file_path}: {exc}")
            return documents

        try:
            for page_idx, page in enumerate(doc, start=1):
                raw_text = page.get_text()
                text = raw_text
                page_ocr_applied = False

                if len(text.strip()) < self.density_threshold and ocr_available:
                    logger.warning(
                        f"Low text density on page {page_idx} of {file_path.name}. Attempting OCR fallback..."
                    )
                    try:
                        image = ocr_service.convert_page_to_image(str(file_path), page_idx)
                        if image:
                            ocr_text = ocr_service.extract_text_from_image(image)
                            if len(ocr_text.strip()) > len(text.strip()):
                                text = ocr_text
                                page_ocr_applied = True
                                logger.info(f"OCR improved text yield for page {page_idx}.")
                    except EnvironmentError as env_err:
                        logger.warning(f"OCR disabled for {file_path.name}: {env_err}")
                        ocr_available = False
                    except Exception as ocr_exc:  # pylint: disable=broad-except
                        logger.error(f"OCR failed for page {page_idx}: {ocr_exc}")

                if text.strip():
                    page_chunks = self._chunk_text(
                        text=text,
                        file_path=str(file_path),
                        file_name=file_path.name,
                        page_num=page_idx,
                        global_chunk_start_idx=doc_chunk_counter,
                        ocr_applied=page_ocr_applied,
                    )
                    documents.extend(page_chunks)
                    doc_chunk_counter += len(page_chunks)
        except Exception as exc:  # pylint: disable=broad-except
            logger.error(f"Error processing PDF {file_path}: {exc}")
        finally:
            doc.close()

        return documents

    def _chunk_text(
        self,
        text: str,
        file_path: str,
        file_name: str,
        page_num: int,
        global_chunk_start_idx: int,
        ocr_applied: bool,
    ) -> List[Dict[str, Any]]:
        chunks: List[Dict[str, Any]] = []
        start = 0
        chunk_idx = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            chunk_content = text[start:end]
            chunk_id = f"{file_name}#P{page_num}:C{chunk_idx}"
            chunks.append(
                {
                    "content": chunk_content,
                    "metadata": {
                        "chunk_id": chunk_id,
                        "file_path": file_path,
                        "file_name": file_name,
                        "page_number": page_num,
                        "chunk_index_page": chunk_idx,
                        "chunk_index_global": global_chunk_start_idx + chunk_idx,
                        "page_char_start": start,
                        "page_char_end": end,
                        "char_count": len(chunk_content),
                        "ocr_applied": ocr_applied,
                        "file_type": "pdf",
                    },
                }
            )
            start += max(self.chunk_size - self.chunk_overlap, 1)
            chunk_idx += 1

        return chunks
