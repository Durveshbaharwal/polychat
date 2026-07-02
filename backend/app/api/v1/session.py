"""
PolyChat — Session API Endpoints
POST /api/v1/session   — Create or retrieve a session
DELETE /api/v1/session — End and clear a session
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.nlp.conversation_manager import get_conversation_manager
from app.schemas import SessionCreateResponse
from app.services.conversation_db_service import get_or_create_session

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Session"])


@router.post(
    "/session",
    response_model=SessionCreateResponse,
    summary="Create a new chat session",
    description="Initialize a new conversation session. Returns a session_id to use in subsequent /chat calls.",
)
async def create_session(
    language: str = Query(default="en", description="Preferred language code"),
    db: AsyncSession = Depends(get_db),
) -> SessionCreateResponse:
    """Create a new session and return its ID."""
    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    # Create in-memory context
    manager = get_conversation_manager()
    manager.create_session(session_id=session_id, language=language)

    # Persist to DB
    await get_or_create_session(db, session_id, language)

    logger.info("Session created: %s (language=%s)", session_id, language)

    return SessionCreateResponse(
        session_id=session_id,
        language=language,
        created_at=now,
    )


@router.delete(
    "/session",
    summary="End a chat session",
    description="Clear session context. The session_id will no longer be tracked.",
)
async def delete_session(
    session_id: str = Query(..., description="Session ID to terminate"),
) -> dict:
    """End a conversation session."""
    manager = get_conversation_manager()
    existed = manager.delete_session(session_id)

    if existed:
        logger.info("Session deleted: %s", session_id)
        return {"success": True, "message": f"Session {session_id} ended."}

    return {"success": False, "message": "Session not found or already expired."}
