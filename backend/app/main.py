"""
PolyChat Backend — FastAPI Application Entry Point

This module creates the FastAPI application, registers middleware, mounts
API routers, and handles startup/shutdown lifecycle events.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import router as api_v1_router
from app.core.config import get_settings
from app.core.exceptions import PolyChatError
from app.core.logging import setup_logging
from app.database.session import init_db
from app.middleware.request_id import RequestIDMiddleware
from app.nlp.pipeline import initialize_nlp_pipeline

# Initialize logging before anything else
setup_logging()
logger = logging.getLogger(__name__)
settings = get_settings()


# ── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Handle application startup and shutdown."""
    logger.info("=" * 60)
    logger.info("Starting %s v%s [%s]", settings.app_name, settings.app_version, settings.env)
    logger.info("=" * 60)

    # Initialize database tables
    await init_db()
    logger.info("Database initialized.")

    # Initialize NLP pipeline (loads model + builds/loads FAISS index)
    await initialize_nlp_pipeline()

    logger.info("Application startup complete. Ready to serve requests.")
    yield

    # Shutdown
    logger.info("Shutting down %s...", settings.app_name)


# ── App Factory ───────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        description=(
            "Multilingual NLP-based Website QA Chatbot API. "
            "Supports English, Hindi, Marathi, and Tamil."
        ),
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ─────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Request ID / Logging ─────────────────────────────────────────────────
    app.add_middleware(RequestIDMiddleware)

    # ── Exception Handlers ────────────────────────────────────────────────────
    @app.exception_handler(PolyChatError)
    async def polychat_exception_handler(request: Request, exc: PolyChatError) -> JSONResponse:
        logger.error("PolyChatError [%s]: %s", exc.code, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                },
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "POLYCHAT_500",
                    "message": "An unexpected error occurred. Please try again.",
                },
            },
        )

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(api_v1_router, prefix=settings.api_v1_prefix)

    # ── Root ──────────────────────────────────────────────────────────────────
    @app.get("/", include_in_schema=False)
    async def root() -> dict:
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": f"{settings.api_v1_prefix}/health",
        }

    return app


app = create_app()
