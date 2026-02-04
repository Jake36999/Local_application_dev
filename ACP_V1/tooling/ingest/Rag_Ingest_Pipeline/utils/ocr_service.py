from PIL import Image
import pytesseract
import logging
from pdf2image import convert_from_path
import os
import sys

logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
# 1. POPPLER PATH (For PDF -> Image conversion)
# Updated to match your specific installation:
POPPLER_PATH = r"C:\Users\jakem\Documents\poppler\poppler-25.12.0\Library\bin"

# 2. TESSERACT PATH (For Image -> Text OCR)
# CRITICAL FOR WINDOWS: Point this to your tesseract.exe
# If you haven't installed it, download from: https://github.com/UB-Mannheim/tesseract/wiki
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def _get_poppler_path():
    """
    Attempts to locate poppler path or returns None to let system PATH handle it.
    """
    if os.name == 'nt': # Only for Windows
        if os.path.exists(POPPLER_PATH):
            return POPPLER_PATH
        
        # Check if user put it in the project folder for ease of use
        local_poppler = os.path.join(os.getcwd(), 'poppler', 'bin')
        if os.path.exists(local_poppler):
            return local_poppler
            
    return None # Default to system PATH

def extract_text_from_image(image_path_or_object) -> str:
    """Extracts text from an image using pytesseract."""
    try:
        if isinstance(image_path_or_object, str):
            img = Image.open(image_path_or_object)
        else:
            img = image_path_or_object
        return pytesseract.image_to_string(img)
    except Exception as e:
        # Check for common Tesseract "not found" errors
        if "tesseract is not installed" in str(e).lower() or "not in your path" in str(e).lower():
             logger.error("Tesseract not found! Please install it and check the path in utils/ocr_service.py")
        else:
            logger.error(f"Error during OCR text extraction: {e}")
        return ""

def convert_page_to_image(pdf_path, page_number):
    """Converts a specific page of a PDF into a PIL Image object using pdf2image."""
    try:
        poppler_path = _get_poppler_path()
        
        # pdf2image uses 1-based indexing for first_page/last_page
        images = convert_from_path(
            pdf_path, 
            first_page=page_number, 
            last_page=page_number,
            poppler_path=poppler_path # Explicitly pass the path
        )
        if images:
            return images[0]
        return None
    except Exception as e:
        if "poppler" in str(e).lower():
            logger.error(f"Poppler not found. Please update POPPLER_PATH in utils/ocr_service.py. Error: {e}")
        else:
            logger.error(f"Error converting PDF page {page_number} to image: {e}")
        return None