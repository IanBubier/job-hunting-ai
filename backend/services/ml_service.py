"""Placeholder ML service."""

import numpy as np


class MLService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._cache = {}

    def encode_text(self, text: str) -> np.ndarray:
        """Generate embedding for input text (placeholder)."""
        # Placeholder: return a zero vector
        return np.zeros(384, dtype=float)

    def calculate_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Placeholder similarity calculation."""
        return 0.0

    def batch_similarity(self, query_emb: np.ndarray, job_embs: list) -> list:
        """Return similarities for a batch of job embeddings (placeholder)."""
        return [0.0 for _ in job_embs]
