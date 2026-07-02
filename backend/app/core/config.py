"""
PolyChat Backend — Application Configuration
Loads all settings from environment variables / .env file.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────────────────────
    app_name: str = "PolyChat"
    app_version: str = "1.0.0"
    env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # ── API ──────────────────────────────────────────────────────────────────
    api_v1_prefix: str = "/api/v1"
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # ── Database ─────────────────────────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./polychat.db"

    # ── NLP ──────────────────────────────────────────────────────────────────
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    vector_index_path: str = "../models/faiss.index"
    faq_data_path: str = "../data/faqs.json"
    top_k_results: int = 5
    confidence_threshold: float = 0.45

    # ── Languages ────────────────────────────────────────────────────────────
    supported_languages: List[str] = ["en", "hi", "mr", "ta", "pa"]
    default_language: str = "en"

    # ── HuggingFace Inference API ────────────────────────────────────────────
    use_inference_api: bool = False
    hf_api_token: Optional[str] = None

    # ── Session ──────────────────────────────────────────────────────────────
    session_timeout: int = 1800  # seconds
    max_history_length: int = 20

    # ── Rate limiting ────────────────────────────────────────────────────────
    rate_limit_requests: int = 60
    rate_limit_window: int = 60  # seconds

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: object) -> List[str]:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v  # type: ignore[return-value]

    @field_validator("supported_languages", mode="before")
    @classmethod
    def parse_languages(cls, v: object) -> List[str]:
        if isinstance(v, str):
            return [lang.strip() for lang in v.split(",")]
        return v  # type: ignore[return-value]

    @property
    def faq_data_file(self) -> Path:
        return Path(self.faq_data_path)

    @property
    def vector_index_file(self) -> Path:
        return Path(self.vector_index_path)

    @property
    def is_production(self) -> bool:
        return self.env == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
