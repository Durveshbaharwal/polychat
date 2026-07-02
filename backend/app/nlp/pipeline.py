"""
PolyChat NLP — Startup Pipeline
Orchestrates model loading, FAQ seeding, and index building on application startup.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from app.core.config import get_settings
from app.nlp.embedding_service import EmbeddingService, get_embedding_service
from app.nlp.faiss_index import FAISSIndex

logger = logging.getLogger(__name__)
settings = get_settings()

# Module-level singleton
_faiss_index: Optional[FAISSIndex] = None


def get_faiss_index() -> FAISSIndex:
    """Return the shared FAISSIndex singleton."""
    global _faiss_index
    if _faiss_index is None:
        raise RuntimeError("FAISS index not initialized. Call initialize_nlp_pipeline() first.")
    return _faiss_index


async def initialize_nlp_pipeline() -> None:
    """
    Initialize all NLP components on application startup.

    Steps:
    1. Instantiate embedding service (model loads lazily on first embed call)
    2. Try to load a persisted FAISS index
    3. If no index, load FAQ data from JSON and build a new one
    """
    global _faiss_index

    logger.info("Initializing NLP pipeline...")

    embedding_service = get_embedding_service()
    _faiss_index = FAISSIndex(embedding_service=embedding_service)

    # Try loading persisted index first (fast path)
    if _faiss_index.load():
        logger.info(
            "Loaded persisted FAISS index with %d entries.", _faiss_index.faq_count
        )
    else:
        # Build index from FAQ data file
        faq_path = settings.faq_data_file
        if not faq_path.exists():
            # Try relative to backend directory (local development)
            alt_path = Path(__file__).parent.parent.parent.parent / "data" / "faqs.json"
            # Try inside the packaged app directory (production container deployment)
            packaged_path = Path(__file__).parent.parent / "faqs.json"
            
            if alt_path.exists():
                faq_path = alt_path
            elif packaged_path.exists():
                faq_path = packaged_path
            else:
                logger.error(
                    "FAQ data file not found at %s or %s or %s",
                    settings.faq_data_file,
                    alt_path,
                    packaged_path,
                )
                return

        logger.info("Building FAISS index from FAQ data: %s", faq_path)
        with open(faq_path, "r", encoding="utf-8") as f:
            faq_data = json.load(f)

        # Trigger model load by building the index
        if not _faiss_index.is_ready:
            _faiss_index.build(faq_data)
            logger.info("NLP pipeline ready. Index contains %d entries.", _faiss_index.faq_count)
    
    # Preload the embedding model into memory so the first request is instant
    logger.info("Preloading embedding model...")
    embedding_service._load_model()
    logger.info("NLP pipeline initialization complete.")
