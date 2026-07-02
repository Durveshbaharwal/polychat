"""
PolyChat — Chat Service (Main Business Logic)

Orchestrates the full chat request flow:
  1. Determine effective language
  2. Retrieve / create conversation context
  3. Build contextual search query
  4. Run semantic search
  5. Build response
  6. Persist conversation asynchronously
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import NLPError, SessionError
from app.nlp.conversation_manager import ConversationManager, Turn, get_conversation_manager
from app.nlp.faiss_index import FAISSIndex, SearchResult
from app.nlp.pipeline import get_faiss_index
from app.nlp.language_detector import detect_language, normalize_language
from app.schemas import ChatRequest, ChatResponse
from app.services.conversation_db_service import save_conversation_turn

logger = logging.getLogger(__name__)
settings = get_settings()

# Fallback responses per language when no good match is found
FALLBACK_MESSAGES = {
    "en": "I'm sorry, I couldn't find a relevant answer to your question. Could you rephrase it? Here are some topics I can help with: pricing, features, support, account management, and technical issues.",
    "hi": "मुझे खेद है, मैं आपके प्रश्न का उचित उत्तर नहीं खोज पाया। क्या आप इसे दूसरे तरीके से पूछ सकते हैं? मैं इन विषयों में मदद कर सकता हूँ: मूल्य निर्धारण, सुविधाएं, सहायता, खाता प्रबंधन, और तकनीकी मुद्दे।",
    "mr": "मला खेद आहे, मला तुमच्या प्रश्नाचे योग्य उत्तर सापडले नाही. तुम्ही वेगळ्या शब्दांत विचारू शकता का? मी या विषयांमध्ये मदत करू शकतो: किंमत, वैशिष्ट्ये, समर्थन, खाते व्यवस्थापन, आणि तांत्रिक समस्या.",
    "ta": "மன்னிக்கவும், உங்கள் கேள்விக்கு பொருத்தமான பதில் கண்டுபிடிக்க முடியவில்லை. வேறு வார்த்தைகளில் கேட்க முடியுமா? நான் இந்த தலைப்புகளில் உதவ முடியும்: விலை, அம்சங்கள், ஆதரவு, கணக்கு நிர்வாகம், மற்றும் தொழில்நுட்ப சிக்கல்கள்.",
    "pa": "ਮੈਨੂੰ ਅਫ਼ਸੋਸ ਹੈ, ਮੈਨੂੰ ਤੁਹਾਡੇ ਸਵਾਲ ਦਾ ਢੁਕਵਾਂ ਜਵਾਬ ਨਹੀਂ ਮਿਲਿਆ। ਕੀ ਤੁਸੀਂ ਇਸਨੂੰ ਹੋਰ ਤਰੀਕੇ ਨਾਲ ਪੁੱਛ ਸਕਦੇ ਹੋ? ਮੈਂ ਇਹਨਾਂ ਵਿਸ਼ਿਆਂ ਵਿੱਚ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ: ਕੀਮਤ, ਵਿਸ਼ੇਸ਼ਤਾਵਾਂ, ਸਹਾਇਤਾ, ਖਾਤਾ ਪ੍ਰਬੰਧਨ, ਅਤੇ ਤਕਨੀਕੀ ਸਮੱਸਿਆਵਾਂ।",
}

DEFAULT_SUGGESTIONS = [
    "What are your pricing plans?",
    "How do I contact support?",
    "What languages do you support?",
    "How do I get started?",
]


class ChatService:
    """Orchestrates the end-to-end chat request."""

    def __init__(
        self,
        faiss_index: Optional[FAISSIndex] = None,
        conversation_manager: Optional[ConversationManager] = None,
    ) -> None:
        self._faiss_index = faiss_index or get_faiss_index()
        self._conversation_manager = conversation_manager or get_conversation_manager()

    async def process(
        self, request: ChatRequest, db: AsyncSession
    ) -> ChatResponse:
        """
        Process a chat message and return a bot response.

        Args:
            request: Validated ChatRequest.
            db: Async database session for persistence.

        Returns:
            ChatResponse with answer, confidence, intent, and suggestions.
        """
        session_id = request.session_id
        user_message = request.message.strip()

        # ── 1. Determine language ────────────────────────────────────────────
        detected_lang, lang_confidence = detect_language(user_message)

        if lang_confidence > 0.8:
            # Use detected language if we're highly confident (e.g. Hindi query in Tamil UI)
            effective_lang = normalize_language(detected_lang)
        elif request.language:
            # Fall back to UI requested language if detection is weak
            effective_lang = normalize_language(request.language)
        else:
            effective_lang = normalize_language(detected_lang)
            
        logger.info(f"Language Resolution: request={request.language}, detected={detected_lang}, conf={lang_confidence}, effective={effective_lang}")

        # ── 2. Get/create conversation context ───────────────────────────────
        ctx = self._conversation_manager.get_or_create(session_id, language=effective_lang)

        # Update language if changed
        if ctx.language != effective_lang:
            ctx.language = effective_lang

        # ── 3. Build contextual query ────────────────────────────────────────
        contextual_query = ctx.build_contextual_query(user_message)
        logger.debug(
            "session=%s original=%r contextual=%r lang=%s",
            session_id, user_message, contextual_query, effective_lang,
        )

        # ── 4. Semantic search ───────────────────────────────────────────────
        try:
            results = self._faiss_index.search(
                query=contextual_query,
                language=effective_lang,
                top_k=settings.top_k_results,
            )
        except NLPError as exc:
            logger.error("Search failed for session %s: %s", session_id, exc)
            results = []

        # ── 5. Select best result ────────────────────────────────────────────
        best: Optional[SearchResult] = None
        is_fallback = True

        if results:
            best = results[0]
            if best.confidence >= settings.confidence_threshold:
                is_fallback = False

        # ── 6. Build response ────────────────────────────────────────────────
        if is_fallback or best is None:
            answer = FALLBACK_MESSAGES.get(effective_lang, FALLBACK_MESSAGES["en"])
            intent = "fallback"
            confidence = best.confidence if best else 0.0
            faq_id = None
            suggestions = DEFAULT_SUGGESTIONS
        else:
            answer = best.answer
            intent = best.intent
            confidence = best.confidence
            faq_id = best.faq_id
            suggestions = best.suggested_questions or DEFAULT_SUGGESTIONS

        # ── 7. Update conversation context ───────────────────────────────────
        user_turn = Turn(
            sender="user",
            message=user_message,
            language=effective_lang,
        )
        bot_turn = Turn(
            sender="bot",
            message=answer,
            language=effective_lang,
            intent=intent,
            confidence=confidence,
        )

        await self._conversation_manager.update_session(
            session_id,
            language=effective_lang,
            current_intent=intent,
            last_question=user_message,
            last_answer=answer,
            user_turn=user_turn,
            bot_turn=bot_turn,
        )

        # ── 8. Persist to DB (fire-and-forget style, catch errors) ──────────
        try:
            await save_conversation_turn(
                db=db,
                session_id=session_id,
                user_message=user_message,
                bot_answer=answer,
                language=effective_lang,
                intent=intent,
                confidence=confidence,
            )
        except Exception as exc:
            logger.warning("Failed to persist conversation turn: %s", exc)

        return ChatResponse(
            session_id=session_id,
            message=user_message,
            answer=answer,
            language=effective_lang,
            detected_language=detected_lang,
            intent=intent,
            confidence=round(confidence, 4),
            is_fallback=is_fallback,
            suggested_questions=suggestions[:3],
            timestamp=datetime.now(timezone.utc),
        )
