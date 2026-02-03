import logging
import chromadb
from pymongo import MongoClient
from config.settings import settings
from utils.embedding_client import EmbeddingClient

logger = logging.getLogger(__name__)

class RetrievalController:
    def __init__(self):
        self.embedding_client = EmbeddingClient()
        
        # ChromaDB (Index)
        self.chroma_client = chromadb.PersistentClient(path=str(settings.CHROMA_DB_PATH))
        self.collection_index = self.chroma_client.get_or_create_collection(name="aletheia_index")
        
        # MongoDB (Canonical Truth)
        self.mongo_client = MongoClient(settings.MONGO_URI)
        self.db = self.mongo_client[settings.DB_NAME]
        self.collection_truth = self.db[settings.COLLECTION_TRUTH]

    def query(self, query: str) -> str:
        """Retrieves context and generates a response."""
        # 1. Embed Query
        query_embedding = self.embedding_client.get_embedding(query)
        if not query_embedding:
            return "Error: Could not process query."

        # 2. Retrieve from ChromaDB
        results = self.collection_index.query(
            query_embeddings=[query_embedding],
            n_results=settings.NUM_RETRIEVAL_RESULTS,
            include=['metadatas']
        )

        # 3. Fetch Full Content from MongoDB (Canonical Truth)
        # We rely on the index to find *where* the data is, but fetch the *clean* data from Mongo.
        context_docs = []
        if results and results['metadatas'] and results['metadatas'][0]:
            for meta in results['metadatas'][0]:
                file_hash = meta.get('file_hash')
                chunk_index = meta.get('chunk_index')
                
                record = self.collection_truth.find_one({
                    "file_hash": file_hash, 
                    "chunk_index": chunk_index
                })
                
                if record:
                    context_docs.append(record['content'])
        
        if not context_docs:
            return "No relevant information found in the archives."

        # 4. Construct Prompt
        context_text = "\n\n---\n\n".join(context_docs)
        return f"Based on the following research:\n\n{context_text}\n\nAnswer: {query}"