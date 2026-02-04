import fitz  # type: ignore[import-untyped]  # PyMuPDF
import pytesseract  # type: ignore[import-untyped]
from PIL import Image
import io
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# --- Configuration (from settings.py) ---
class PDFSettings:
    OCR_TEXT_DENSITY_THRESHOLD = 100
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50

settings = PDFSettings()

# --- OCR Service (from ocr_service.py) ---
def _convert_page_to_image(doc, page_number: int):
    try:
        page = doc.load_page(page_number) 
        pix = page.get_pixmap()
        return pix.tobytes("png")
    except Exception as e:
        logger.error(f"Image conversion failed for page {page_number}: {e}")
        return None

def _extract_text_from_image(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        return pytesseract.image_to_string(image)
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        return ""

# --- Core Processor (Adapted from pdf_processor.py) ---
def scan_pdf(file_path: str) -> Dict[str, Any]:
    """
    Scans a PDF, applying OCR if text density is low.
    Returns a structured dictionary of the document content.
    """
    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}

    documents = []
    full_text = []
    
    try:
        doc = fitz.open(path)
        for i, page in enumerate(doc):
            text = page.get_text()
            
            # Check if OCR is needed
            if len(text.strip()) < settings.OCR_TEXT_DENSITY_THRESHOLD:
                logger.info(f"Page {i+1} requires OCR.")
                img_bytes = _convert_page_to_image(doc, i)
                if img_bytes:
                    ocr_text = _extract_text_from_image(img_bytes)
                    if len(ocr_text) > len(text):
                        text = ocr_text
            
            full_text.append(text)
            
            # Create chunks (simplified for the tool output)
            documents.append({
                "page": i + 1,
                "content": text[:200] + "..." if len(text) > 200 else text, # Preview only for the report
                "length": len(text)
            })
            
        doc.close()
        
        return {
            "status": "success",
            "filename": path.name,
            "total_pages": len(documents),
            "full_text_preview": "\n".join(full_text)[:1000], # First 1000 chars
            "pages": documents
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}