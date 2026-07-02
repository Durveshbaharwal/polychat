"""
PolyChat NLP — Embedding Service
Wraps sentence-transformers with lazy loading and simple caching.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Dict, List, Optional

import numpy as np

from app.core.config import get_settings
from app.core.exceptions import EmbeddingError

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingService:
    """
    Generates dense vector embeddings using a multilingual sentence transformer.

    The model is loaded once on first use (lazy loading) to avoid blocking
    application startup.
    """

    def __init__(self) -> None:
        self._model = None
        self._cache: Dict[str, np.ndarray] = {}
        self._model_name = settings.embedding_model

    def _load_model(self) -> None:
        """Load the sentence transformer model (called once)."""
        if settings.use_inference_api:
            return

        if self._model is not None:
            return

        logger.info("Loading embedding model: %s", self._model_name)
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name)
            logger.info("Embedding model loaded successfully.")
        except Exception as exc:
            raise EmbeddingError(
                f"Failed to load embedding model '{self._model_name}': {exc}"
            ) from exc

    def _query_inference_api(self, inputs: List[str] | str) -> list:
        """Query HuggingFace Serverless Inference API for vector embeddings."""
        import json
        import urllib.request
        import urllib.error

        model = self._model_name
        if "/" not in model:
            model = f"sentence-transformers/{model}"

        url = f"https://api-inference.huggingface.co/models/{model}"
        headers = {
            "Content-Type": "application/json",
        }
        if settings.hf_api_token:
            headers["Authorization"] = f"Bearer {settings.hf_api_token}"

        data = json.dumps({"inputs": inputs}).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers)

        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            raise EmbeddingError(f"HuggingFace API HTTP Error: {e.code} - {err_body}")
        except Exception as e:
            raise EmbeddingError(f"HuggingFace API connection failed: {e}")

    def _cache_key(self, text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def embed(self, text: str) -> np.ndarray:
        """
        Generate a single embedding vector for the given text.

        Args:
            text: Input text to embed.

        Returns:
            numpy array of shape (embedding_dim,)
        """
        if settings.use_inference_api:
            key = self._cache_key(text)
            if key in self._cache:
                return self._cache[key]

            res = self._query_inference_api(text)
            if isinstance(res, list) and len(res) > 0 and isinstance(res[0], list):
                vector = np.array(res[0], dtype=np.float32)
            else:
                vector = np.array(res, dtype=np.float32)

            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
            self._cache[key] = vector
            return vector

        self._load_model()

        key = self._cache_key(text)
        if key in self._cache:
            return self._cache[key]

        try:
            vector: np.ndarray = self._model.encode(  # type: ignore[union-attr]
                text,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            self._cache[key] = vector
            return vector
        except Exception as exc:
            raise EmbeddingError(f"Embedding generation failed: {exc}") from exc

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of input texts.

        Returns:
            numpy array of shape (len(texts), embedding_dim)
        """
        if settings.use_inference_api:
            res = self._query_inference_api(texts)
            vectors = np.array(res, dtype=np.float32)
            # Normalize along axis 1
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            return vectors / norms

        self._load_model()

        try:
            vectors: np.ndarray = self._model.encode(  # type: ignore[union-attr]
                texts,
                normalize_embeddings=True,
                show_progress_bar=False,
                batch_size=32,
            )
            return vectors
        except Exception as exc:
            raise EmbeddingError(f"Batch embedding failed: {exc}") from exc

    @property
    def is_loaded(self) -> bool:
        return self._model is not None or settings.use_inference_api

    def clear_cache(self) -> None:
        self._cache.clear()


# Module-level singleton
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Return the shared EmbeddingService singleton."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
