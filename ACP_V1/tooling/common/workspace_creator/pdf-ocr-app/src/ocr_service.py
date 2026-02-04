def convert_page_to_image(pdf_path: str, page_number: int) -> Any:
    """
    Converts a specific page of a PDF document to an image.
    
    Args:
        pdf_path (str): The path to the PDF file.
        page_number (int): The page number to convert (1-indexed).
    
    Returns:
        Any: The image representation of the PDF page, or None if conversion fails.
    """
    import fitz  # PyMuPDF

    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(page_number - 1)  # fitz uses 0-indexing
        pix = page.get_pixmap()
        image = pix.tobytes("png")  # Convert to PNG format
        doc.close()
        return image
    except Exception as e:
        logger.error(f"Error converting page {page_number} of {pdf_path} to image: {e}")
        return None


def extract_text_from_image(image: Any) -> str:
    """
    Extracts text from an image using OCR.
    
    Args:
        image (Any): The image from which to extract text.
    
    Returns:
        str: The extracted text.
    """
    import pytesseract
    from PIL import Image
    import io

    try:
        image = Image.open(io.BytesIO(image))
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        logger.error(f"Error extracting text from image: {e}")
        return ""