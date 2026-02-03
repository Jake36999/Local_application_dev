import os
import logging
from pathlib import Path
from typing import Final, Optional
from dotenv import load_dotenv

# Load environmental variables
load_dotenv()

# Global Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aletheia_system.log'),
        logging.StreamHandler()
    ]
)

class Settings:
    """
    Centralized configuration engine for Aletheia RAG Infrastructure.
    """
    # Section 1: Directory Management
    # Resolves to the parent of 'config', which is the root 'Ingest_pipeline_V2'
    BASE_DIR: Final[Path] = Path(__file__).resolve().parent.parent
    
    DATA_DIR: Final[Path] = BASE_DIR / "data"
    RAW_LANDING_DIR: Final[Path] = DATA_DIR / "raw_landing"
    PROCESSED_ARCHIVE_DIR: Final[Path] = DATA_DIR / "processed_archive"
    BACKUP_DIR: Final[Path] = PROCESSED_ARCHIVE_DIR / "backups"
    
    # Section 2: Storage Paths
    CHROMA_DB_PATH: Final[Path] = BASE_DIR / "memory" / "chroma_db"
    EMBEDDING_CACHE_DIR: Final[Path] = BASE_DIR / "memory" / ".embedding_cache"
    USAGE_LOG_PATH: Final[Path] = BASE_DIR / "logs" / "usage_stats.json"

    # Section 3: Database (MongoDB)
    MONGO_URI: Final[str] = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME: Final[str] = "aletheia_memory"
    COLLECTION_TRUTH: Final[str] = "canonical_truth"
    COLLECTION_TRACES: Final[str] = "reasoning_traces"

    # Section 4: Inference (LM Studio)
    LM_STUDIO_BASE_URL: Final[str] = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")
    EMBEDDING_MODEL: Final[str] = "nomic-ai/nomic-embed-text-v1.5-GGUF"
    NOMIC_PREFIX: Final[str] = "search_document: " 

    # Section 5: RAG & OCR Logic
    CHUNK_SIZE: Final[int] = 1500 
    CHUNK_OVERLAP: Final[int] = 200
    OCR_TEXT_DENSITY_THRESHOLD: int = 50 # Characters per page below which OCR is triggered
    NUM_RETRIEVAL_RESULTS: int = 5

    def validate_settings(self):
        """Ensures directories exist and critical settings are present."""
        paths = [
            self.DATA_DIR, self.RAW_LANDING_DIR, self.PROCESSED_ARCHIVE_DIR, 
            self.BACKUP_DIR, self.CHROMA_DB_PATH, self.USAGE_LOG_PATH.parent,
            self.EMBEDDING_CACHE_DIR
        ]
        for p in paths:
            p.mkdir(parents=True, exist_ok=True)
        
        if not self.MONGO_URI:
            raise ValueError("MONGO_URI environment variable is missing.")

settings = Settings()
settings.validate_settings()