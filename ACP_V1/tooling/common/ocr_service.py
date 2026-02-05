from PIL import Image
import importlib
import logging
from pdf2image import convert_from_path
import os
import sys
from typing import Any, cast

pytesseract = cast(Any, importlib.import_module("pytesseract"))

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
    """Extracts text from an image using pytesseract.

    Raises:
        EnvironmentError: when Tesseract is missing/misconfigured.
        Exception: for other OCR errors.
    """
    try:
        if isinstance(image_path_or_object, str):
            img = Image.open(image_path_or_object)
        else:
            img = image_path_or_object
        return pytesseract.image_to_string(img)
    except Exception as e:
        msg = str(e).lower()
        if "tesseract is not installed" in msg or "not in your path" in msg:
            error_msg = (
                f"Tesseract not found or misconfigured at '{pytesseract.pytesseract.tesseract_cmd}'. "
                "Install it or update utils/ocr_service.py"
            )
            logger.critical(error_msg)
            raise EnvironmentError(error_msg) from e
        logger.error(f"Error during OCR text extraction: {e}")
        raise

def convert_page_to_image(pdf_path, page_number):
    """Converts a specific page of a PDF into a PIL Image using pdf2image.

    Raises:
        EnvironmentError: when Poppler is missing/misconfigured.
        Exception: for other conversion errors.
    """
    try:
        poppler_path = _get_poppler_path()
        poppler_kwargs = {"poppler_path": poppler_path} if poppler_path else {}

        images = convert_from_path(
            pdf_path,
            first_page=page_number,
            last_page=page_number,
            **poppler_kwargs
        )
        if images:
            return images[0]
        return None
    except Exception as e:
        if "poppler" in str(e).lower():
            error_msg = (
                f"Poppler not found or misconfigured at '{POPPLER_PATH}'. "
                "Install it or update utils/ocr_service.py"
            )
            logger.critical(error_msg)
            raise EnvironmentError(error_msg) from e
        logger.error(f"Error converting PDF page {page_number} to image: {e}")
        raise