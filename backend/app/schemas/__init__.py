"""
PolyChat — Pydantic Request/Response Schemas
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


# ── Common ────────────────────────────────────────────────────────────────────

class SuccessResponse(BaseModel):
    """Generic success wrapper."""

    success: bool = True
    data: Any = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


# ── Session ───────────────────────────────────────────────────────────────────

class SessionCreateResponse(BaseModel):
    session_id: str
    language: str
    created_at: datetime


class SessionData(BaseModel):
    session_id: str
    language: str = "en"
    current_intent: Optional[str] = None
    last_question: Optional[str] = None
    last_answer: Optional[str] = None
    history: List[Dict[str, str]] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ── Chat ──────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    """Incoming chat message from the user."""

    session_id: str = Field(..., min_length=1, max_length=36, description="Session UUID")
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    language: Optional[str] = Field(
        default=None,
        description="Override language (en/hi/mr/ta). Auto-detected if omitted.",
    )

    @field_validator("message")
    @classmethod
    def strip_message(cls, v: str) -> str:
        return v.strip()

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            supported = {"en", "hi", "mr", "ta", "pa"}
            if v not in supported:
                raise ValueError(f"Language must be one of: {supported}")
        return v


class SuggestedQuestion(BaseModel):
    text: str
    intent: Optional[str] = None


class ChatResponse(BaseModel):
    """Bot response sent back to the widget."""

    session_id: str
    message: str
    answer: str
    language: str
    detected_language: str
    intent: Optional[str] = None
    confidence: float
    is_fallback: bool = False
    suggested_questions: List[str] = Field(default_factory=list)
    timestamp: datetime


# ── Feedback ──────────────────────────────────────────────────────────────────

class FeedbackRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=36)
    faq_id: Optional[str] = None
    question: str = Field(..., min_length=1, max_length=2000)
    answer: str = Field(..., min_length=1)
    rating: bool = Field(..., description="True = helpful, False = not helpful")
    language: str = Field(default="en")
    comment: Optional[str] = Field(default=None, max_length=1000)


class FeedbackResponse(BaseModel):
    success: bool = True
    message: str = "Feedback recorded. Thank you!"
    feedback_id: str


# ── Health ────────────────────────────────────────────────────────────────────

class ComponentHealth(BaseModel):
    status: str  # "ok" | "error" | "degraded"
    message: Optional[str] = None


class HealthResponse(BaseModel):
    status: str  # "ok" | "degraded" | "error"
    version: str
    environment: str
    components: Dict[str, ComponentHealth]
    timestamp: datetime


# ── Language ──────────────────────────────────────────────────────────────────

class LanguageInfo(BaseModel):
    code: str
    name: str
    native_name: str
    flag: str


class LanguagesResponse(BaseModel):
    supported: List[LanguageInfo]
    default: str
