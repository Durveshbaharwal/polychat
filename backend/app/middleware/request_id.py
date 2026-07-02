"""
PolyChat — Request ID & Logging Middleware
"""

from __future__ import annotations

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Injects a unique X-Request-ID header on every request and logs it."""

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = int((time.perf_counter() - start) * 1000)

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{elapsed_ms}ms"

        logger.info(
            "%s %s %d %dms [%s]",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
            request_id,
        )

        return response
