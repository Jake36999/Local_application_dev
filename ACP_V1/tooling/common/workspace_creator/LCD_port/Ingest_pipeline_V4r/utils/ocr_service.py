import importlib
import logging
import os
from typing import Any, Optional, cast

from pdf2image import convert_from_path
from PIL import Image

pytesseract = cast(Any, importlib.import_module("pytesseract"))

logger = logging.getLogger(__name__)

# Configure these paths for your environment or via env vars.
POPPLER_DEFAULT = r"C:\Users\jakem\Documents\poppler\poppler-25.12.0\Library\bin"
TESSERACT_DEFAULT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

POPPLER_PATH = os.getenv("POPPLER_PATH", POPPLER_DEFAULT)
TESSERACT_CMD = os.getenv("TESSERACT_CMD", TESSERACT_DEFAULT)
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def _ensure_tesseract_configured() -> None:
    """Validate Tesseract path and raise if missing on Windows."""
    if os.name == "nt" and not os.path.exists(TESSERACT_CMD):
        error_msg = (
            f"Tesseract not found at '{TESSERACT_CMD}'. Set TESSERACT_CMD env or update utils/ocr_service.py"
        )
        logger.critical(error_msg)
        raise EnvironmentError(error_msg)


def _get_poppler_path() -> Optional[str]:
    """Resolve Poppler path (env overrides default)."""
    env_path = os.getenv("POPPLER_PATH")
    if env_path:
        if os.path.exists(env_path):
            return env_path
        raise EnvironmentError(f"POPPLER_PATH env set to '{env_path}' but directory not found.")

    if os.name == "nt":
        if os.path.exists(POPPLER_DEFAULT):
            return POPPLER_DEFAULT
        local_poppler = os.path.join(os.getcwd(), "poppler", "bin")
        if os.path.exists(local_poppler):
            return local_poppler
        raise EnvironmentError(
            "Poppler not found. Set POPPLER_PATH env var or update utils/ocr_service.py to point to poppler/bin."
        )

    # Non-Windows: let pdf2image rely on system PATH
    return None


def extract_text_from_image(image_path_or_object: Any) -> str:
    """Extract text via Tesseract; raise when Tesseract is unavailable."""
    _ensure_tesseract_configured()
    try:
        img = Image.open(image_path_or_object) if isinstance(image_path_or_object, str) else image_path_or_object
        return pytesseract.image_to_string(img)
    except Exception as exc:  # pylint: disable=broad-except
        msg = str(exc).lower()
        if "tesseract is not installed" in msg or "not in your path" in msg:
            error_msg = (
                f"Tesseract not found or misconfigured at '{pytesseract.pytesseract.tesseract_cmd}'. "
                "Install it or update utils/ocr_service.py"
            )
            logger.critical(error_msg)
            raise EnvironmentError(error_msg) from exc
        logger.error(f"Error during OCR text extraction: {exc}")
        raise


def convert_page_to_image(pdf_path: str, page_number: int) -> Optional[Any]:
    """Convert a single PDF page to an image using pdf2image."""
    try:
        poppler_path = _get_poppler_path()
        if poppler_path:
            images = convert_from_path(
                pdf_path,
                first_page=page_number,
                last_page=page_number,
                poppler_path=poppler_path,
            )
        else:
            images = convert_from_path(
                pdf_path,
                first_page=page_number,
                last_page=page_number,
            )
        if images:
            return images[0]
        return None
    except Exception as exc:  # pylint: disable=broad-except
        if "poppler" in str(exc).lower():
            error_msg = (
                f"Poppler not found or misconfigured at '{POPPLER_PATH}'. "
                "Install it or update utils/ocr_service.py"
            )
            logger.critical(error_msg)
            raise EnvironmentError(error_msg) from exc
        logger.error(f"Error converting PDF page {page_number} to image: {exc}")
        raise
