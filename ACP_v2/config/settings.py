import os
from pathlib import Path
from config import settings as config_settings



class Settings:
    def __init__(self):
        self.COLLECTION_TRUTH: str = os.environ.get('COLLECTION_TRUTH', 'truth_collection')
        self.COLLECTION_TRACES: str = os.environ.get('COLLECTION_TRACES', 'traces')
        self.NUM_RETRIEVAL_RESULTS: int = int(os.environ.get('NUM_RETRIEVAL_RESULTS', 5))
        self.OCR_TEXT_DENSITY_THRESHOLD: int = int(os.environ.get('OCR_TEXT_DENSITY_THRESHOLD', 100))
        self.CHUNK_SIZE: int = int(os.environ.get('CHUNK_SIZE', 500))
        self.CHUNK_OVERLAP: int = int(os.environ.get('CHUNK_OVERLAP', 50))
        self.MONGO_URI: str = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
        self.DB_NAME: str = os.environ.get('DB_NAME', 'aletheia_db')
        self.CHROMA_DB_PATH: Path = Path(os.environ.get('CHROMA_DB_PATH', './chroma_db'))
        self.RAW_LANDING_DIR: Path = Path(os.environ.get('RAW_LANDING_DIR', './staging/incoming'))
        self.LM_STUDIO_BASE_URL: str = os.environ.get('LM_STUDIO_BASE_URL', 'http://localhost:1234')
        self.EMBEDDING_MODEL: str = os.environ.get('EMBEDDING_MODEL', 'nomic-embed-text-v1.5')
        self.NOMIC_PREFIX: str = os.environ.get('NOMIC_PREFIX', 'search_document: ')
        self.SSE_METRIC_KEY: str = os.environ.get('SSE_METRIC_KEY', 'sse_metric')
        self.STABILITY_METRIC_KEY: str = os.environ.get('STABILITY_METRIC_KEY', 'stability_metric')
        self.HASH_KEY: str = os.environ.get('HASH_KEY', 'hash_key')

# Provide a module-level settings instance for import
app_settings = Settings()