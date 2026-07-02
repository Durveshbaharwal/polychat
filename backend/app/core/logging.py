"""
PolyChat Backend — Structured JSON Logging
"""

from __future__ import annotations

import json
import logging
import sys
import time
from typing import Any, Dict

from app.core.config import get_settings


class JSONFormatter(logging.Formatter):
    """Format log records as JSON lines for production."""

    def format(self, record: logging.LogRecord) -> str:
        log_object: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_object["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "request_id"):
            log_object["request_id"] = record.request_id
        if hasattr(record, "session_id"):
            log_object["session_id"] = record.session_id
        return json.dumps(log_object, ensure_ascii=False)


def setup_logging() -> None:
    """Configure root logger based on application settings."""
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)

    if settings.is_production:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Silence noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("faiss").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger."""
    return logging.getLogger(name)
