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
        # Use OpenAI-compatible endpoint for LM Studio
        # Ensure base_url is just host:port, endpoint is /v1/embeddings
        self.base_url = f"{settings.LM_STUDIO_BASE_URL}/v1/embeddings"
        self.last_activity = time.time()

        # Automatically prime LM Studio model for embeddings
        try:
            load_url = f"{settings.LM_STUDIO_BASE_URL}/api/v1/models/load"
            payload = {"model": settings.EMBEDDING_MODEL}
            resp = requests.post(load_url, json=payload, timeout=30)
            if resp.status_code == 200:
                logger.info(f"LM Studio model primed: {settings.EMBEDDING_MODEL}")
            else:
                logger.warning(f"LM Studio model priming failed: {resp.text}")
        except Exception as e:
            logger.warning(f"LM Studio model priming error: {e}")

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
                resp_json = response.json()
                if "data" not in resp_json:
                    logger.error(f"Embedding API response missing 'data' key: {resp_json}")
                    raise KeyError("'data' key missing in embedding response")
                if not isinstance(resp_json["data"], list) or not resp_json["data"]:
                    logger.error(f"Embedding API response 'data' is not a non-empty list: {resp_json}")
                    raise ValueError("'data' key is not a non-empty list")
                embedding = resp_json["data"][0].get("embedding")
                if not isinstance(embedding, list):
                    logger.error(f"Embedding API response missing 'embedding' in first data element: {resp_json}")
                    raise KeyError("'embedding' key missing in first data element")
                return embedding
            except Exception as e:
                wait = (attempt + 1) * 2
                logger.warning(f"Embedding failed (Attempt {attempt+1}): {e}. Retrying in {wait}s...")
                try:
                    logger.debug(f"Full embedding API response: {response.text if 'response' in locals() else 'No response'}")
                except Exception:
                    pass
                time.sleep(wait)
        logger.error(f"Failed to retrieve embedding after retries for text snippet.")
        return None

    def clear_cache(self):
        """Clears the embedding cache."""
        self.get_embedding.cache_clear()