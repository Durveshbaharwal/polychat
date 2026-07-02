"""
PolyChat NLP — Conversation Context Manager
Maintains per-session state in memory with SQLite persistence for history.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class Turn:
    """A single conversation turn (one message from user or bot)."""

    sender: str  # "user" | "bot"
    message: str
    language: str
    intent: Optional[str] = None
    confidence: Optional[float] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ConversationContext:
    """Full context for a conversation session."""

    session_id: str
    language: str = "en"
    current_intent: Optional[str] = None
    last_question: Optional[str] = None
    last_answer: Optional[str] = None
    history: List[Turn] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_turn(self, turn: Turn) -> None:
        """Append a turn, pruning oldest if over limit."""
        self.history.append(turn)
        max_len = settings.max_history_length
        if len(self.history) > max_len:
            self.history = self.history[-max_len:]
        self.updated_at = datetime.now(timezone.utc)

    def build_contextual_query(self, new_question: str) -> str:
        """
        Build an enhanced query by combining context with the new question.

        For follow-up questions (short, referential), prepend the last question
        to improve semantic matching.

        Example:
            last: "What are your office timings?"
            new: "What about Saturday?"
            result: "What are your office timings? What about Saturday?"
        """
        if not self.last_question:
            return new_question

        # Heuristic: if new question is short and contains referential words,
        # it's likely a follow-up
        follow_up_indicators = [
            "what about", "and", "also", "how about", "then", "same", "those",
            "that", "it", "they", "them", "there", "when", "where", "who",
        ]
        q_lower = new_question.lower().strip()
        is_follow_up = (
            len(new_question.split()) <= 3
            or any(q_lower.startswith(word) for word in follow_up_indicators)
        )

        if is_follow_up:
            return f"{self.last_question} {new_question}"

        return new_question

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "language": self.language,
            "current_intent": self.current_intent,
            "last_question": self.last_question,
            "last_answer": self.last_answer,
            "history_count": len(self.history),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class ConversationManager:
    """
    Thread-safe in-memory store for conversation contexts.

    Uses asyncio.Lock per session to prevent race conditions.
    """

    def __init__(self) -> None:
        self._sessions: Dict[str, ConversationContext] = {}
        self._locks: Dict[str, asyncio.Lock] = {}

    def _get_lock(self, session_id: str) -> asyncio.Lock:
        if session_id not in self._locks:
            self._locks[session_id] = asyncio.Lock()
        return self._locks[session_id]

    def create_session(
        self, session_id: Optional[str] = None, language: str = "en"
    ) -> ConversationContext:
        """Create a new conversation session."""
        sid = session_id or str(uuid.uuid4())
        ctx = ConversationContext(session_id=sid, language=language)
        self._sessions[sid] = ctx
        logger.debug("Created session: %s (language=%s)", sid, language)
        return ctx

    def get_session(self, session_id: str) -> Optional[ConversationContext]:
        """Return an existing session, or None if not found."""
        return self._sessions.get(session_id)

    def get_or_create(
        self, session_id: str, language: str = "en"
    ) -> ConversationContext:
        """Return existing session or create a new one."""
        if session_id in self._sessions:
            return self._sessions[session_id]
        return self.create_session(session_id, language)

    async def update_session(
        self,
        session_id: str,
        *,
        language: Optional[str] = None,
        current_intent: Optional[str] = None,
        last_question: Optional[str] = None,
        last_answer: Optional[str] = None,
        user_turn: Optional[Turn] = None,
        bot_turn: Optional[Turn] = None,
    ) -> ConversationContext:
        """Update session fields and optionally append turns."""
        async with self._get_lock(session_id):
            ctx = self.get_or_create(session_id, language or "en")

            if language is not None:
                ctx.language = language
            if current_intent is not None:
                ctx.current_intent = current_intent
            if last_question is not None:
                ctx.last_question = last_question
            if last_answer is not None:
                ctx.last_answer = last_answer
            if user_turn is not None:
                ctx.add_turn(user_turn)
            if bot_turn is not None:
                ctx.add_turn(bot_turn)

            return ctx

    def delete_session(self, session_id: str) -> bool:
        """Remove a session. Returns True if it existed."""
        existed = session_id in self._sessions
        self._sessions.pop(session_id, None)
        self._locks.pop(session_id, None)
        return existed

    def session_count(self) -> int:
        return len(self._sessions)


# Module-level singleton
_conversation_manager: Optional[ConversationManager] = None


def get_conversation_manager() -> ConversationManager:
    """Return the shared ConversationManager singleton."""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
    return _conversation_manager
