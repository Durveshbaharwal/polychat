"""
PolyChat — Feedback Service
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Feedback
from app.schemas import FeedbackRequest, FeedbackResponse

logger = logging.getLogger(__name__)


class FeedbackService:
    """Handles saving user feedback on bot responses."""

    async def save(self, request: FeedbackRequest, db: AsyncSession) -> FeedbackResponse:
        """Persist feedback to database."""
        feedback_id = str(uuid.uuid4())

        feedback = Feedback(
            id=feedback_id,
            session_id=request.session_id,
            faq_id=request.faq_id,
            question=request.question,
            answer=request.answer,
            rating=request.rating,
            language=request.language,
            comment=request.comment,
            created_at=datetime.now(timezone.utc),
        )

        db.add(feedback)
        logger.info(
            "Feedback saved: id=%s session=%s rating=%s",
            feedback_id,
            request.session_id,
            "helpful" if request.rating else "not_helpful",
        )

        return FeedbackResponse(
            success=True,
            message="Feedback recorded. Thank you!",
            feedback_id=feedback_id,
        )
