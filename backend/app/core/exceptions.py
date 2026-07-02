"""
PolyChat Backend — Custom Exception Hierarchy
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class PolyChatError(Exception):
    """Base exception for all PolyChat errors."""

    code: str = "POLYCHAT_000"
    status_code: int = 500
    message: str = "An unexpected error occurred."

    def __init__(
        self,
        message: Optional[str] = None,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.message = message or self.__class__.message
        self.code = code or self.__class__.code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(PolyChatError):
    """Raised when request validation fails."""

    code = "POLYCHAT_400"
    status_code = 400
    message = "Invalid request data."


class NotFoundError(PolyChatError):
    """Raised when a requested resource does not exist."""

    code = "POLYCHAT_404"
    status_code = 404
    message = "Resource not found."


class NLPError(PolyChatError):
    """Raised when NLP pipeline encounters an error."""

    code = "POLYCHAT_NLP_001"
    status_code = 500
    message = "NLP processing failed."


class EmbeddingError(NLPError):
    """Raised when embedding generation fails."""

    code = "POLYCHAT_NLP_002"
    message = "Failed to generate embeddings."


class SearchError(NLPError):
    """Raised when vector search fails."""

    code = "POLYCHAT_NLP_003"
    message = "Semantic search failed."


class LanguageDetectionError(NLPError):
    """Raised when language detection fails."""

    code = "POLYCHAT_NLP_004"
    message = "Language detection failed."


class SessionError(PolyChatError):
    """Raised for session-related errors."""

    code = "POLYCHAT_SESSION_001"
    status_code = 400
    message = "Session error."


class DatabaseError(PolyChatError):
    """Raised when database operations fail."""

    code = "POLYCHAT_DB_001"
    status_code = 500
    message = "Database operation failed."
