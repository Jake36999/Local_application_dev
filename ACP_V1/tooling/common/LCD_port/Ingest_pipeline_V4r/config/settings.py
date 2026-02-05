class Settings:
    OCR_TEXT_DENSITY_THRESHOLD = 100  # Minimum text density before triggering OCR fallback
    CHUNK_SIZE = 500  # Characters per chunk when splitting text
    CHUNK_OVERLAP = 50  # Overlap between consecutive chunks


settings = Settings()
