"""PolyChat — API v1 router aggregator."""

from fastapi import APIRouter

from app.api.v1 import chat, feedback, health, language, session

router = APIRouter()

router.include_router(chat.router)
router.include_router(feedback.router)
router.include_router(session.router)
router.include_router(language.router)
router.include_router(health.router)
