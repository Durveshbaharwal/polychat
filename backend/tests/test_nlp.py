"""
PolyChat — Unit Tests for NLP Pipeline
"""

from __future__ import annotations

import pytest

from app.nlp.language_detector import detect_language, normalize_language


class TestLanguageDetector:
    """Tests for language detection."""

    def test_detect_english(self) -> None:
        lang, conf = detect_language("What are your pricing plans?")
        assert lang == "en"
        assert conf > 0.5

    def test_detect_hindi(self) -> None:
        lang, conf = detect_language("आपकी मूल्य योजनाएं क्या हैं?")
        assert lang == "hi"

    def test_detect_tamil(self) -> None:
        lang, conf = detect_language("உங்கள் விலை திட்டங்கள் என்ன?")
        assert lang == "ta"

    def test_empty_string_fallback(self) -> None:
        lang, conf = detect_language("")
        assert lang == "en"
        assert conf == 0.0

    def test_normalize_unsupported(self) -> None:
        result = normalize_language("fr")
        assert result == "en"

    def test_normalize_supported(self) -> None:
        assert normalize_language("hi") == "hi"
        assert normalize_language("mr") == "mr"
        assert normalize_language("ta") == "ta"
        assert normalize_language("en") == "en"


class TestConversationContext:
    """Tests for conversation context and follow-up detection."""

    def test_follow_up_detection_short_question(self) -> None:
        from app.nlp.conversation_manager import ConversationContext

        ctx = ConversationContext(
            session_id="test",
            last_question="What are your office timings?",
        )
        query = ctx.build_contextual_query("What about Saturday?")
        assert "office timings" in query
        assert "Saturday" in query

    def test_normal_question_no_injection(self) -> None:
        from app.nlp.conversation_manager import ConversationContext

        ctx = ConversationContext(
            session_id="test",
            last_question="What are your office timings?",
        )
        query = ctx.build_contextual_query(
            "How do I integrate the chatbot widget into my website?"
        )
        # Long question should not get context injected
        assert "office timings" not in query

    def test_no_last_question(self) -> None:
        from app.nlp.conversation_manager import ConversationContext

        ctx = ConversationContext(session_id="test")
        query = ctx.build_contextual_query("What are your pricing plans?")
        assert query == "What are your pricing plans?"


class TestConversationManager:
    """Tests for session lifecycle."""

    def test_create_and_retrieve_session(self) -> None:
        from app.nlp.conversation_manager import ConversationManager

        mgr = ConversationManager()
        ctx = mgr.create_session("sess-001", language="hi")
        assert ctx.session_id == "sess-001"
        assert ctx.language == "hi"

        retrieved = mgr.get_session("sess-001")
        assert retrieved is not None
        assert retrieved.session_id == "sess-001"

    def test_delete_session(self) -> None:
        from app.nlp.conversation_manager import ConversationManager

        mgr = ConversationManager()
        mgr.create_session("sess-002")
        assert mgr.delete_session("sess-002") is True
        assert mgr.get_session("sess-002") is None

    def test_history_pruning(self) -> None:
        from app.nlp.conversation_manager import ConversationContext, Turn

        ctx = ConversationContext(session_id="test")
        for i in range(25):  # Exceeds max_history_length=20
            ctx.add_turn(Turn(sender="user", message=f"msg {i}", language="en"))
        assert len(ctx.history) == 20
