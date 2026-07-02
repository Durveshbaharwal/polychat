"""
PolyChat — Chat API Endpoint
POST /api/v1/chat
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Send a chat message",
    description="Submit a user message and receive a semantically matched answer from the FAQ knowledge base.",
)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """
    Process a user message and return the chatbot response.

    - Detects language automatically if not specified
    - Maintains conversation context for follow-up questions
    - Returns answer in the detected/selected language
    - Includes confidence score and suggested follow-up questions
    """
    service = ChatService()
    return await service.process(request, db)
