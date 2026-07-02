"""
PolyChat — Language API Endpoint
GET /api/v1/languages
"""

from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings
from app.nlp.language_detector import LANGUAGE_INFO
from app.schemas import LanguageInfo, LanguagesResponse

router = APIRouter(tags=["Language"])
settings = get_settings()


@router.get(
    "/languages",
    response_model=LanguagesResponse,
    summary="Get supported languages",
    description="Returns the list of languages supported by the chatbot.",
)
async def get_languages() -> LanguagesResponse:
    """Return all supported languages with metadata."""
    supported = [
        LanguageInfo(
            code=code,
            name=info["name"],
            native_name=info["native_name"],
            flag=info["flag"],
        )
        for code, info in LANGUAGE_INFO.items()
        if code in settings.supported_languages
    ]

    return LanguagesResponse(
        supported=supported,
        default=settings.default_language,
    )
