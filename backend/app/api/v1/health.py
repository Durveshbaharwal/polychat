"""
PolyChat — Health Check Endpoint
GET /api/v1/health
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.database.session import get_db
from app.nlp.pipeline import _faiss_index
from app.schemas import ComponentHealth, HealthResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns the health status of all system components.",
)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Check system health across all components."""
    components: dict[str, ComponentHealth] = {}
    overall_ok = True

    # ── Database ─────────────────────────────────────────────────────────────
    try:
        await db.execute(text("SELECT 1"))
        components["database"] = ComponentHealth(status="ok")
    except Exception as exc:
        components["database"] = ComponentHealth(status="error", message=str(exc))
        overall_ok = False
        logger.error("Database health check failed: %s", exc)

    # ── NLP / FAISS Index ─────────────────────────────────────────────────────
    try:
        if _faiss_index is not None and _faiss_index.is_ready:
            components["nlp_index"] = ComponentHealth(
                status="ok",
                message=f"{_faiss_index.faq_count} FAQ entries indexed",
            )
        else:
            components["nlp_index"] = ComponentHealth(
                status="degraded",
                message="Index not yet built",
            )
            overall_ok = False
    except Exception as exc:
        components["nlp_index"] = ComponentHealth(status="error", message=str(exc))
        overall_ok = False

    # ── Embedding Model ───────────────────────────────────────────────────────
    try:
        from app.nlp.embedding_service import get_embedding_service
        svc = get_embedding_service()
        status = "ok" if svc.is_loaded else "degraded"
        components["embedding_model"] = ComponentHealth(
            status=status,
            message=f"Model: {settings.embedding_model}",
        )
    except Exception as exc:
        components["embedding_model"] = ComponentHealth(status="error", message=str(exc))

    overall_status = "ok" if overall_ok else "degraded"

    return HealthResponse(
        status=overall_status,
        version=settings.app_version,
        environment=settings.env,
        components=components,
        timestamp=datetime.now(timezone.utc),
    )
