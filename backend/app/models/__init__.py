"""
PolyChat — SQLAlchemy Models (all in one module for import simplicity)
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class FAQCategory(Base):
    """Category for grouping FAQ entries."""

    __tablename__ = "faq_category"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    faqs: Mapped[list["FAQ"]] = relationship("FAQ", back_populates="category")


class FAQ(Base):
    """FAQ knowledge base entry with per-language answers."""

    __tablename__ = "faq"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    category_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("faq_category.id"), nullable=True
    )
    intent: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)

    # Per-language answers
    answer_en: Mapped[str] = mapped_column(Text, nullable=False)
    answer_hi: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    answer_mr: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    answer_ta: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    answer_pa: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Suggested follow-up questions (JSON stored as text)
    suggested_questions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    embedding_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now, nullable=False
    )

    category: Mapped[Optional[FAQCategory]] = relationship(
        "FAQCategory", back_populates="faqs"
    )
    feedbacks: Mapped[list["Feedback"]] = relationship("Feedback", back_populates="faq")

    def get_answer(self, language: str) -> str:
        """Return answer in requested language, falling back to English."""
        lang_map = {
            "en": self.answer_en,
            "hi": self.answer_hi,
            "mr": self.answer_mr,
            "ta": self.answer_ta,
            "pa": self.answer_pa,
        }
        return lang_map.get(language) or self.answer_en


class Session(Base):
    """Chat session record."""

    __tablename__ = "session"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    current_intent: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now, nullable=False
    )

    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation", back_populates="session"
    )
    feedbacks: Mapped[list["Feedback"]] = relationship(
        "Feedback", back_populates="session"
    )


class Conversation(Base):
    """A single message turn in a conversation."""

    __tablename__ = "conversation"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("session.id"), nullable=False, index=True
    )
    sender: Mapped[str] = mapped_column(String(10), nullable=False)  # "user" | "bot"
    message: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    intent: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, nullable=False
    )

    session: Mapped[Session] = relationship("Session", back_populates="conversations")


class Feedback(Base):
    """User feedback on a bot response."""

    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    session_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("session.id"), nullable=True
    )
    faq_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("faq.id"), nullable=True
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[bool] = mapped_column(Boolean, nullable=False)  # True=helpful
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, nullable=False
    )

    session: Mapped[Optional[Session]] = relationship(
        "Session", back_populates="feedbacks"
    )
    faq: Mapped[Optional[FAQ]] = relationship("FAQ", back_populates="feedbacks")


class AuditLog(Base):
    """Lightweight request audit log."""

    __tablename__ = "audit_log"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    request_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    endpoint: Mapped[str] = mapped_column(String(200), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    session_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, nullable=False
    )
