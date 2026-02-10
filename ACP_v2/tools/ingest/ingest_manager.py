import os
import sys
from pathlib import Path
import shutil

# Add project root to sys.path for robust import resolution
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))
import logging
from typing import cast, Sequence, List, Dict, Any, Mapping
from pathlib import Path
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
import chromadb
from datetime import datetime
from config.settings import settings
# FIX: Consistent imports
from tools.common.pdf_processor import PDFProcessor
from tools.common.codebase_processor import CodebaseProcessor

from tools.common.embedding_client import EmbeddingClient
from tools.common.metadata_extractor import extract_document_metadata

logger = logging.getLogger(__name__)

class IngestManager:
    """
    Manages the complete ingestion pipeline for PDF and Text/Code documents.
    """
    def __init__(self):
        # Initialize Databases
        self.mongo_client: Any = MongoClient(settings.MONGO_URI)
        self.db = self.mongo_client[settings.DB_NAME]
        self.collection_truth = self.db[settings.COLLECTION_TRUTH]
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=str(settings.CHROMA_DB_PATH))
        self.collection_index = self.chroma_client.get_or_create_collection(name="aletheia_index")
        
        # Initialize Core Engines
        self.pdf_processor = PDFProcessor()
        self.codebase_processor = CodebaseProcessor()
        self.embedder = EmbeddingClient()

        # Ensure processed/failed directories exist
        self.processed_dir = settings.RAW_LANDING_DIR.parent / "processed"
        self.failed_dir = settings.RAW_LANDING_DIR.parent / "failed"
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.failed_dir.mkdir(parents=True, exist_ok=True)
        
    def process_file(self, file_path: Path) -> bool:
        """
        Processes a single file through the ingestion pipeline.
        Routes to the appropriate processor based on file type.
        """
        try:
            logger.info(f"Processing: {file_path.name}")
            # 1. Select Processor Strategy
            if file_path.suffix.lower() == '.pdf':
                chunks = list(self.pdf_processor.process_file(file_path))
            else:
                chunks = list(self.codebase_processor.process_file(file_path))
            if not chunks:
                logger.warning(f"No usable content found in {file_path.name}")
                raise ValueError("No text extracted")
            # 2. Vectorization and Persistence
            chroma_ids = []
            chroma_embeddings = []
            chroma_metadatas = []
            mongo_docs = []
            for i, chunk in enumerate(chunks):
                content_text = chunk["content"]
                chunk_meta = chunk["metadata"]
                file_hash = chunk_meta.get('file_name', file_path.name)
                doc_id = f"{file_hash}_{i}"
                vector = self.embedder.get_embedding(content_text)
                if not vector:
                    continue
                mongo_docs.append({
                    "file_hash": file_hash,
                    "chunk_index": i,
                    "content": content_text,
                    "metadata": chunk_meta,
                    "ingested_at": datetime.utcnow().isoformat()
                })
                chroma_ids.append(doc_id)
                chroma_embeddings.append(vector)
                chroma_metadatas.append({
                    "file_hash": file_hash,
                    "chunk_index": i,
                    "page": chunk_meta.get('page_number', 0),
                    "file_name": chunk_meta.get('file_name', 'unknown')
                })
            if mongo_docs:
                try:
                    self.collection_truth.insert_many(mongo_docs, ordered=False)
                except BulkWriteError as bwe:
                    duplicates = [e for e in bwe.details['writeErrors'] if e['code'] == 11000]
                    if len(duplicates) == len(mongo_docs):
                        logger.info(f"Skipping {file_path.name}: All chunks already exist in DB.")
                        shutil.move(str(file_path), str(self.processed_dir / file_path.name))
                        return True
                    elif duplicates:
                        logger.info(f"Partial insert for {file_path.name}: {len(duplicates)} duplicates skipped.")
                    else:
                        error_msg = str(bwe).encode('ascii', 'replace').decode('ascii')
                        logger.warning(f"MongoDB Bulk Write Error: {error_msg}")
            if chroma_ids:
                try:
                    self.collection_index.add(
                        ids=chroma_ids,
                        embeddings=cast(Sequence[float], chroma_embeddings),
                        metadatas=cast(List[Mapping[str, Any]], chroma_metadatas),
                        documents=[d['content'] for d in mongo_docs]
                    )
                except Exception as e:
                    logger.warning(f"ChromaDB Write Warning for {file_path.name}: {e}")
            logger.info(f"Successfully processed: {file_path.name}")
            shutil.move(str(file_path), str(self.processed_dir / file_path.name))
            return True
        except Exception as e:
            safe_error = str(e).encode('ascii', 'replace').decode('ascii')
            logger.error(f"Error processing file {file_path.name}: {safe_error}")
            try:
                shutil.move(str(file_path), str(self.failed_dir / file_path.name))
            except Exception as move_err:
                logger.error(f"Failed to move {file_path.name} to failed dir: {move_err}")
            return False
    
    def process_all(self):
        """Processes all supported files in the raw landing directory recursively."""
        allowed_suffixes = {".pdf", ".txt", ".py", ".md", ".json", ".sh", ".ps1"}
        all_files = []
        for ext in allowed_suffixes:
            for path in settings.RAW_LANDING_DIR.rglob(f"*{ext}"):
                if path.is_file() and path.suffix.lower() in allowed_suffixes:
                    all_files.append(path)

        if not all_files:
            logger.info("No files found to process.")
            return 0

        processed_count = 0
        for f in all_files:
            if self.process_file(f):
                processed_count += 1

        logger.info(f"Ingestion completed. Processed {processed_count}/{len(all_files)}.")
        return processed_count

if __name__ == "__main__":
    manager = IngestManager()
    count = manager.process_all()
    print(f"Ingestion finished. Processed {count} files.")
