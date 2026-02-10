
from typing import Any
class Settings:
	OCR_TEXT_DENSITY_THRESHOLD: int
	CHUNK_SIZE: int
	CHUNK_OVERLAP: int
	MONGO_URI: str
	DB_NAME: str
	COLLECTION_TRUTH: str
	CHROMA_DB_PATH: Any
	RAW_LANDING_DIR: Any
	LM_STUDIO_BASE_URL: str
	EMBEDDING_MODEL: str
	NOMIC_PREFIX: str

settings: Settings
