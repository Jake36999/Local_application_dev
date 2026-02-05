class Settings:
    OCR_TEXT_DENSITY_THRESHOLD = 100  # Minimum text density to avoid OCR
    CHUNK_SIZE = 500  # Number of characters per chunk
    CHUNK_OVERLAP = 50  # Number of overlapping characters between chunks

settings = Settings()