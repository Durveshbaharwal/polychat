# PolyChat Backend Dockerfile
# Multi-stage build: deps → app

FROM python:3.12-slim AS base

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Dependency stage ──────────────────────────────────────────────────────────
FROM base AS deps
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Application stage ─────────────────────────────────────────────────────────
FROM deps AS app

# Copy application source
COPY app/ ./app/

# Create directories for data and models
RUN mkdir -p /data /models

# Non-root user for security
RUN useradd -m -u 1001 polychat && \
    chown -R polychat:polychat /app /data /models
USER polychat

# Environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENV=production \
    DEBUG=false \
    LOG_LEVEL=INFO \
    DATABASE_URL=sqlite+aiosqlite:////data/polychat.db \
    VECTOR_INDEX_PATH=/models/faiss.index \
    FAQ_DATA_PATH=/data/faqs.json

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
