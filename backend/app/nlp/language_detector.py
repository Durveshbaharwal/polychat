"""
PolyChat NLP — Language Detection Service
Uses langdetect with a deterministic seed. Falls back to English gracefully.
"""

from __future__ import annotations

import logging
from typing import Tuple

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Supported language codes
SUPPORTED_LANGUAGES = {"en", "hi", "mr", "ta", "pa"}

# Human-readable language names
LANGUAGE_INFO = {
    "en": {"name": "English", "native_name": "English", "flag": "🇬🇧"},
    "hi": {"name": "Hindi", "native_name": "हिंदी", "flag": "🇮🇳"},
    "mr": {"name": "Marathi", "native_name": "मराठी", "flag": "🇮🇳"},
    "ta": {"name": "Tamil", "native_name": "தமிழ்", "flag": "🇮🇳"},
    "pa": {"name": "Punjabi", "native_name": "ਪੰਜਾਬੀ", "flag": "🇮🇳"},
}


def detect_language(text: str) -> Tuple[str, float]:
    """
    Detect the language of the input text.

    Returns:
        Tuple of (language_code, confidence).
        Falls back to ("en", 0.0) on any error.
    """
    if not text or not text.strip():
        return settings.default_language, 0.0

    try:
        from langdetect import DetectorFactory, detect_langs

        DetectorFactory.seed = 0  # Make detection deterministic

        results = detect_langs(text.strip())
        if not results:
            return settings.default_language, 0.0

        # Find best supported language
        for result in results:
            lang_code = result.lang
            confidence = float(result.prob)

            # langdetect returns "zh-cn" for Chinese, "pt" for Portuguese, etc.
            # We only care about our 4 supported languages.
            if lang_code in SUPPORTED_LANGUAGES:
                logger.debug("Detected language=%s confidence=%.3f", lang_code, confidence)
                return lang_code, confidence

        # No supported language detected — use the top result's confidence but
        # fall back to English
        top_confidence = float(results[0].prob)
        logger.debug(
            "Detected unsupported language=%s, falling back to 'en'", results[0].lang
        )
        return settings.default_language, top_confidence

    except Exception as exc:
        logger.warning("Language detection failed: %s. Defaulting to 'en'.", exc)
        return settings.default_language, 0.0


def normalize_language(lang_code: str) -> str:
    """Normalize a language code to a supported code, defaulting to English."""
    if lang_code in SUPPORTED_LANGUAGES:
        return lang_code
    return settings.default_language
