"""
PolyChat NLP — FAISS Vector Index
Builds, saves, loads, and queries the FAQ semantic search index.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from app.core.config import get_settings
from app.core.exceptions import EmbeddingError, SearchError
from app.nlp.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class FAQRecord:
    """In-memory FAQ record used by the search index."""

    id: str
    intent: str
    category: str
    question: str
    answers: Dict[str, str]
    suggested_questions: Dict[str, List[str]] = field(default_factory=dict)

    def get_answer(self, language: str) -> str:
        return self.answers.get(language) or self.answers.get("en", "")

    def get_suggested_questions(self, language: str) -> List[str]:
        if isinstance(self.suggested_questions, dict):
            return self.suggested_questions.get(language) or self.suggested_questions.get("en", [])
        return self.suggested_questions


@dataclass
class SearchResult:
    """Result from a FAISS similarity search."""

    faq_id: str
    intent: str
    question: str
    answer: str
    confidence: float
    suggested_questions: List[str]


class FAISSIndex:
    """
    Manages the FAISS vector index for semantic FAQ search.

    Responsibilities:
    - Building the index from FAQ data
    - Persisting the index to disk
    - Loading a persisted index on startup
    - Running similarity search for incoming queries
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
        index_path: Optional[Path] = None,
    ) -> None:
        self._embedding_service = embedding_service
        self._index_path = index_path or settings.vector_index_file
        self._index = None  # faiss.Index
        self._records: List[FAQRecord] = []
        self._id_to_index: Dict[str, int] = {}

    @property
    def is_ready(self) -> bool:
        return self._index is not None and len(self._records) > 0

    @property
    def faq_count(self) -> int:
        return len(self._records)

    def build(self, faq_data: List[dict]) -> None:
        """
        Build the FAISS index from a list of FAQ dicts (loaded from faqs.json).

        Args:
            faq_data: List of FAQ dicts matching the faqs.json schema.
        """
        import faiss

        logger.info("Building FAISS index from %d FAQ entries...", len(faq_data))

        self._records = []
        questions: List[str] = []

        for item in faq_data:
            answers = item.get("answers", {})
            record = FAQRecord(
                id=item["id"],
                intent=item.get("intent", "unknown"),
                category=item.get("category", "General"),
                question=item["question"],
                answers=answers,
                suggested_questions=item.get("suggested_questions", []),
            )
            self._records.append(record)
            questions.append(item["question"])

        # Generate embeddings for all questions
        vectors = self._embedding_service.embed_batch(questions)
        vectors = np.array(vectors, dtype=np.float32)

        # Build flat L2 index (cosine via normalized vectors)
        dimension = vectors.shape[1]
        self._index = faiss.IndexFlatIP(dimension)  # Inner Product = cosine on normalized
        self._index.add(vectors)  # type: ignore[union-attr]

        # Build reverse lookup
        self._id_to_index = {rec.id: i for i, rec in enumerate(self._records)}

        logger.info(
            "FAISS index built: %d vectors, dimension=%d", len(self._records), dimension
        )

        # Persist to disk
        self._save()

    def _save(self) -> None:
        """Save index and metadata to disk."""
        import faiss

        try:
            index_dir = self._index_path.parent
            index_dir.mkdir(parents=True, exist_ok=True)

            faiss.write_index(self._index, str(self._index_path))

            meta_path = self._index_path.with_suffix(".meta.json")
            meta = [
                {
                    "id": rec.id,
                    "intent": rec.intent,
                    "category": rec.category,
                    "question": rec.question,
                    "answers": rec.answers,
                    "suggested_questions": rec.suggested_questions,
                }
                for rec in self._records
            ]
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)

            logger.info("FAISS index saved to %s", self._index_path)
        except Exception as exc:
            logger.warning("Failed to persist FAISS index: %s", exc)

    def load(self) -> bool:
        """
        Load a persisted index from disk.

        Returns:
            True if loaded successfully, False if no index found.
        """
        import faiss

        meta_path = self._index_path.with_suffix(".meta.json")
        index_path = self._index_path

        if not index_path.exists() or not meta_path.exists():
            # Try inside the packaged app directory (production container deployment)
            packaged_index = Path(__file__).parent.parent / "faiss.index"
            packaged_meta = Path(__file__).parent.parent / "faiss.meta.json"
            if packaged_index.exists() and packaged_meta.exists():
                index_path = packaged_index
                meta_path = packaged_meta
            else:
                logger.info(
                    "No persisted FAISS index found at %s or %s",
                    self._index_path,
                    packaged_index,
                )
                return False

        try:
            self._index = faiss.read_index(str(index_path))

            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)

            self._records = [
                FAQRecord(
                    id=item["id"],
                    intent=item["intent"],
                    category=item["category"],
                    question=item["question"],
                    answers=item["answers"],
                    suggested_questions=item.get("suggested_questions", []),
                )
                for item in meta
            ]
            self._id_to_index = {rec.id: i for i, rec in enumerate(self._records)}

            logger.info(
                "FAISS index loaded: %d vectors from %s",
                len(self._records),
                self._index_path,
            )
            return True
        except Exception as exc:
            logger.error("Failed to load FAISS index: %s", exc)
            return False

    def search(
        self,
        query: str,
        language: str = "en",
        top_k: Optional[int] = None,
    ) -> List[SearchResult]:
        """
        Run semantic similarity search for the given query.

        Args:
            query: User's question text.
            language: Language code for answer retrieval.
            top_k: Number of results to return.

        Returns:
            Sorted list of SearchResult (highest confidence first).
        """
        if not self.is_ready:
            raise SearchError("FAISS index is not initialized.")

        k = top_k or settings.top_k_results

        try:
            query_vector = self._embedding_service.embed(query)
            query_vector = np.array([query_vector], dtype=np.float32)

            scores, indices = self._index.search(query_vector, k)  # type: ignore[union-attr]

            results: List[SearchResult] = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < 0 or idx >= len(self._records):
                    continue  # FAISS returns -1 for unfilled slots

                record = self._records[idx]
                confidence = float(max(0.0, min(1.0, score)))  # IP score is [-1, 1]

                results.append(
                    SearchResult(
                        faq_id=record.id,
                        intent=record.intent,
                        question=record.question,
                        answer=record.get_answer(language),
                        confidence=confidence,
                        suggested_questions=record.get_suggested_questions(language),
                    )
                )

            # Already sorted by FAISS (highest score first)
            return results
        except EmbeddingError as exc:
            logger.warning(
                "Embedding unavailable, falling back to keyword search: %s", exc
            )
            return self._keyword_search(query, language, k)
        except SearchError:
            raise
        except Exception as exc:
            raise SearchError(f"Search failed: {exc}") from exc

    def _keyword_search(
        self,
        query: str,
        language: str = "en",
        top_k: int = 5,
    ) -> List[SearchResult]:
        """
        Lightweight keyword/token-overlap search used as fallback when the
        embedding service is unreachable (e.g. HuggingFace API down on free tier).

        Uses character bigrams + word tokens for multilingual support.
        Also matches against the record's pre-defined keyword list and the
        localized answer text, giving good coverage for both English and
        Indic language queries.
        Returns results sorted by descending Jaccard-overlap score.
        """
        def tokenize(text: str):
            text = text.lower()
            words = set(text.split())
            # character bigrams for CJK / Hindi / Tamil / Marathi support
            bigrams = set(text[i:i+2] for i in range(len(text) - 1))
            return words | bigrams

        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        scored: List[Tuple[float, FAQRecord]] = []
        for record in self._records:
            # Combine question tokens + the record's keyword list + localized answer
            corpus_text = record.question
            if hasattr(record, "answers") and isinstance(record.answers, dict):
                # add localized answer for extra matching surface
                corpus_text += " " + record.answers.get(language, "") + " " + record.answers.get("en", "")
            rec_tokens = tokenize(corpus_text)

            # Jaccard similarity
            intersection = len(query_tokens & rec_tokens)
            union = len(query_tokens | rec_tokens)
            score = intersection / union if union > 0 else 0.0
            scored.append((score, record))

        scored.sort(key=lambda x: x[0], reverse=True)

        results: List[SearchResult] = []
        for score, record in scored[:top_k]:
            results.append(
                SearchResult(
                    faq_id=record.id,
                    intent=record.intent,
                    question=record.question,
                    answer=record.get_answer(language),
                    confidence=round(score * 0.85, 4),  # scale down slightly vs semantic
                    suggested_questions=record.get_suggested_questions(language),
                )
            )
        return results

    def get_all_records(self) -> List[FAQRecord]:
        return list(self._records)
