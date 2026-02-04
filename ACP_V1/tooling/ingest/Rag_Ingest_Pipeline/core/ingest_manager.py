import logging
from pathlib import Path
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
import chromadb
from datetime import datetime
from config.settings import settings
# FIX: Consistent imports
from core.pdf_processor import PDFProcessor
from core.codebase_processor import CodebaseProcessor  # Matches lowercase filename
from utils.embedding_client import EmbeddingClient

logger = logging.getLogger(__name__)

class IngestManager:
    """
    Manages the complete ingestion pipeline for PDF and Text/Code documents.
    """
    def __init__(self):
        # Initialize Databases
        self.mongo_client = MongoClient(settings.MONGO_URI)
        self.db = self.mongo_client[settings.DB_NAME]
        self.collection_truth = self.db[settings.COLLECTION_TRUTH]
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=str(settings.CHROMA_DB_PATH))
        self.collection_index = self.chroma_client.get_or_create_collection(name="aletheia_index")
        
        # Initialize Core Engines
        self.pdf_processor = PDFProcessor()
        self.codebase_processor = CodebaseProcessor()
        self.embedder = EmbeddingClient()
        
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
                # Fallback to codebase processor for .py, .txt, .md, .json, etc.
                chunks = list(self.codebase_processor.process_file(file_path))
            
            if not chunks:
                logger.warning(f"No usable content found in {file_path.name}")
                return False
            
            # 2. Vectorization and Persistence
            chroma_ids = []
            chroma_embeddings = []
            chroma_metadatas = []
            mongo_docs = []
            
            for i, chunk in enumerate(chunks):
                content_text = chunk["content"]
                chunk_meta = chunk["metadata"]
                
                # Generate unique ID
                file_hash = chunk_meta.get('file_name', file_path.name)
                doc_id = f"{file_hash}_{i}"
                
                # Get Embedding
                vector = self.embedder.get_embedding(content_text)
                if not vector:
                    continue
                
                # Prepare Mongo Document
                mongo_docs.append({
                    "file_hash": file_hash,
                    "chunk_index": i,
                    "content": content_text,
                    "metadata": chunk_meta,
                    "ingested_at": datetime.utcnow().isoformat()
                })

                # Prepare Chroma Data
                chroma_ids.append(doc_id)
                chroma_embeddings.append(vector)
                chroma_metadatas.append({
                    "file_hash": file_hash,
                    "chunk_index": i,
                    "page": chunk_meta.get('page_number', 0),
                    "file_name": chunk_meta.get('file_name', 'unknown')
                })

            # Bulk Write to Mongo (Robust Duplicate Handling)
            if mongo_docs:
                try:
                    # ordered=False continues processing even if one insert fails (e.g. duplicate)
                    self.collection_truth.insert_many(mongo_docs, ordered=False)
                except BulkWriteError as bwe:
                    # Log duplicates as info, actual errors as warning
                    duplicates = [e for e in bwe.details['writeErrors'] if e['code'] == 11000]
                    if len(duplicates) == len(mongo_docs):
                        logger.info(f"Skipping {file_path.name}: All chunks already exist in DB.")
                        return True
                    elif duplicates:
                        logger.info(f"Partial insert for {file_path.name}: {len(duplicates)} duplicates skipped.")
                    else:
                        # Sanitize error message to prevent UnicodeEncodeError in Windows consoles
                        error_msg = str(bwe).encode('ascii', 'replace').decode('ascii')
                        logger.warning(f"MongoDB Bulk Write Error: {error_msg}")

            # Bulk Write to Chroma
            if chroma_ids:
                try:
                    self.collection_index.add(
                        ids=chroma_ids,
                        embeddings=chroma_embeddings,
                        metadatas=chroma_metadatas,
                        documents=[d['content'] for d in mongo_docs]
                    )
                except Exception as e:
                    # Chroma might error on duplicates, but usually updates/upserts.
                    # If it fails, log and continue.
                    logger.warning(f"ChromaDB Write Warning for {file_path.name}: {e}")
                    
            logger.info(f"Successfully processed: {file_path.name}")
            return True
            
        except Exception as e:
            # Catch-all to ensure one bad file doesn't crash the whole batch
            # Sanitize error message to prevent UnicodeEncodeError
            safe_error = str(e).encode('ascii', 'replace').decode('ascii')
            logger.error(f"Error processing file {file_path.name}: {safe_error}")
            return False
    
    def process_all(self):
        """Processes all supported files in the raw landing directory recursively."""
        extensions = ["*.pdf", "*.txt", "*.py", "*.md", "*.json", "*.sh", "*.ps1"]
        all_files = []
        
        for ext in extensions:
            all_files.extend(list(settings.RAW_LANDING_DIR.rglob(ext)))
            
        if not all_files:
            logger.info(f"No supported files found in {settings.RAW_LANDING_DIR}")
            return
            
        logger.info(f"Starting ingestion of {len(all_files)} files.")
        processed_count = sum(1 for f in all_files if self.process_file(f))
        logger.info(f"Ingestion completed. Processed {processed_count}/{len(all_files)}.")