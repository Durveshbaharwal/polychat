"""
PolyChat — Feedback API Endpoint
POST /api/v1/feedback
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas import FeedbackRequest, FeedbackResponse
from app.services.feedback_service import FeedbackService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Feedback"])


@router.post(
    "/feedback",
    response_model=FeedbackResponse,
    summary="Submit response feedback",
    description="Submit a thumbs-up or thumbs-down rating on a bot response.",
)
async def submit_feedback(
    request: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
) -> FeedbackResponse:
    """Store user feedback (helpful / not helpful) for a bot response."""
    service = FeedbackService()
    return await service.save(request, db)
