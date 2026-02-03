import requests
import logging
import time
from typing import List, Optional
from functools import lru_cache
from config.settings import settings

logger = logging.getLogger(__name__)

class EmbeddingClient:
    """
    Interface for local LM Studio embeddings with caching and resource awareness.
    """
    def __init__(self):
        self.base_url = f"{settings.LM_STUDIO_BASE_URL}/embeddings"
        self.last_activity = time.time()

    def _check_resource_status(self):
        """
        Placeholder for checking system health or triggering model unloads.
        Could be extended to use LM Studio's /v1/models endpoint to check TTL.
        """
        self.last_activity = time.time()
        # In a JIT strategy, we could ping a custom management script here
        pass

    @lru_cache(maxsize=2048) # Increased cache size for better performance
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generates a vector with LRU caching.
        Note: Nomic models require the 'search_document: ' prefix.
        """
        self._check_resource_status()
        
        prefixed_text = f"{settings.NOMIC_PREFIX}{text}"
        payload = {"input": prefixed_text, "model": settings.EMBEDDING_MODEL}
        
        # Implement internal retry logic
        for attempt in range(3):
            try:
                response = requests.post(self.base_url, json=payload, timeout=30)
                response.raise_for_status()
                return response.json()["data"][0]["embedding"]
            except Exception as e:
                wait = (attempt + 1) * 2
                logger.warning(f"Embedding failed (Attempt {attempt+1}): {e}. Retrying in {wait}s...")
                time.sleep(wait)
        
        logger.error(f"Failed to retrieve embedding after retries for text snippet.")
        return None

    def clear_cache(self):
        """Clears the embedding cache."""
        self.get_embedding.cache_clear()