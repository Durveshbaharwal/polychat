"""
PolyChat — Conversation DB Service
Persists conversation turns to SQLite asynchronously.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Conversation, Session

logger = logging.getLogger(__name__)


async def get_or_create_session(db: AsyncSession, session_id: str, language: str = "en") -> Session:
    """Return an existing DB session record or create one."""
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()

    if session is None:
        session = Session(id=session_id, language=language)
        db.add(session)
        await db.flush()

    return session


async def save_conversation_turn(
    db: AsyncSession,
    session_id: str,
    user_message: str,
    bot_answer: str,
    language: str,
    intent: Optional[str],
    confidence: float,
) -> None:
    """Persist a user+bot turn pair to the database."""
    now = datetime.now(timezone.utc)

    # Ensure session exists
    await get_or_create_session(db, session_id, language)

    # User turn
    user_conv = Conversation(
        id=str(uuid.uuid4()),
        session_id=session_id,
        sender="user",
        message=user_message,
        language=language,
        created_at=now,
    )
    # Bot turn
    bot_conv = Conversation(
        id=str(uuid.uuid4()),
        session_id=session_id,
        sender="bot",
        message=bot_answer,
        language=language,
        confidence=confidence,
        intent=intent,
        created_at=now,
    )

    db.add(user_conv)
    db.add(bot_conv)
    # Session commit handled by get_db() dependency
