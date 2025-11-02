from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
import logging

logger = logging.getLogger(__name__)

class MLService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize with lightweight SBERT model
        Model size: 82MB, inference time: ~10ms per text
        384-dimensional embeddings
        """
        self.model = SentenceTransformer(model_name)
        self._cache = {}  # Cache for frequent queries, format - {hash(text): embedding}
        self.max_cache_size = 1000  # Limit cache size to avoid excessive memory use

    def encode_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for input text
        Args:
            text: input string to encode
        Returns:
            a 384-dimensional numpy array
        """
        cache_key = hash(text)
        if cache_key in self._cache:
            return self._cache[cache_key]

        embedding = self.model.encode(
            text, convert_to_numpy=True, normalize_embeddings=True
        )

        # Simple cache eviction policy: remove oldest entry if cache is full
        if len(self._cache) >= self.max_cache_size:
            self._cache.pop(next(iter(self._cache)))
        self._cache[cache_key] = embedding
        return embedding

    def calculate_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings
        Args:
            emb1: first embedding
            emb2: second embedding
        Returns:
            similarity score between [0.0, 1.0]
        """
        return float(np.dot(emb1, emb2))

    def batch_similarity(
        self, query_emb: np.ndarray, job_embs: List[np.ndarray]
    ) -> List[float]:
        """
        Calculate similarity for multiple jobs efficiently
        Args:
            query_emb: user profile embedding
            job_embs: list of job embeddings
        Returns:
            list of similarity scores
        """
        if not job_embs:
            return []
        job_matrix = np.vstack(job_embs)  # Shape: (num_jobs, embedding_dim)
        dot_products = np.dot(job_matrix, query_emb)  # Shape: (num_jobs,)
        return dot_products.tolist()
