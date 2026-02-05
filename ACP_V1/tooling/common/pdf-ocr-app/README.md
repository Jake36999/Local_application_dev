# PDF OCR Application

## Overview
The PDF OCR Application is a Python-based tool designed to process PDF files with Optical Character Recognition (OCR) capabilities. It extracts text from PDF documents, applies OCR when necessary, and organizes the extracted text into manageable chunks for further processing.

## Features
- Extracts text from PDF files page-by-page.
- Applies OCR to scanned pages with low text density.
- Chunks extracted text into configurable sizes for easier handling.

## Installation
To set up the project, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd pdf-ocr-app
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
To process a PDF file, you can use the `PDFProcessor` class from the `pdf_processor.py` module. Here’s a basic example:

```python
from src.pdf_processor import PDFProcessor
from pathlib import Path

processor = PDFProcessor()
documents = processor.process_file(Path('path/to/your/file.pdf'))

for doc in documents:
    print(doc['content'])
```

## Configuration
You can adjust the settings for the application in `src/config/settings.py`. Key settings include:
- `OCR_TEXT_DENSITY_THRESHOLD`: The threshold for determining if OCR should be applied.
- `CHUNK_SIZE`: The size of each text chunk.
- `CHUNK_OVERLAP`: The overlap between chunks.

## Running Tests
To ensure everything is working correctly, run the tests located in the `tests` directory:
```
pytest tests/test_pdf_processor.py
```

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.