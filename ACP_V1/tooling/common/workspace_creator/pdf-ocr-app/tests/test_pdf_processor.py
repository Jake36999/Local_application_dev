import pytest
from pathlib import Path
from src.pdf_processor import PDFProcessor

@pytest.fixture
def pdf_processor():
    return PDFProcessor()

def test_process_file(pdf_processor):
    test_pdf_path = Path("tests/test_files/test_document.pdf")  # Adjust the path as necessary
    documents = pdf_processor.process_file(test_pdf_path)
    
    assert isinstance(documents, list)
    assert len(documents) > 0  # Ensure some documents are returned

def test_chunk_text(pdf_processor):
    text = "This is a sample text for chunking."
    file_path = str(Path("tests/test_files/test_document.pdf"))
    file_name = "test_document.pdf"
    page_num = 1
    chunks = pdf_processor._chunk_text(text, file_path, file_name, page_num)
    
    assert isinstance(chunks, list)
    assert len(chunks) > 0  # Ensure chunks are created
    assert all("content" in chunk for chunk in chunks)
    assert all("metadata" in chunk for chunk in chunks)