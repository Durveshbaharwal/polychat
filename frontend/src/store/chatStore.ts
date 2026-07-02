// PolyChat — Zustand State Store

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Language, Message, Theme } from '@/types';
import { createSession, sendMessage, submitFeedback, getLanguages } from '@/services/api';
import type { LanguageInfo } from '@/types';

let messageIdCounter = 0;
const generateId = (): string => `msg_${Date.now()}_${++messageIdCounter}`;

interface ChatStore {
  // State
  sessionId: string | null;
  messages: Message[];
  language: Language;
  availableLanguages: LanguageInfo[];
  theme: Theme;
  isOpen: boolean;
  isLoading: boolean;
  isTyping: boolean;
  error: string | null;
  hasGreeted: boolean;

  // Actions
  initSession: () => Promise<void>;
  sendMessage: (text: string) => Promise<void>;
  setLanguage: (lang: Language) => void;
  toggleTheme: () => void;
  toggleWidget: () => void;
  openWidget: () => void;
  closeWidget: () => void;
  submitFeedback: (messageId: string, rating: boolean) => Promise<void>;
  clearError: () => void;
  loadLanguages: () => Promise<void>;
}

const GREETING_MESSAGES: Record<Language, string> = {
  en: "👋 Hello! I'm PolyChat, your multilingual virtual assistant. I can help you with pricing, features, support, and more. How can I assist you today?",
  hi: "👋 नमस्ते! मैं PolyChat हूँ, आपका बहुभाषी सहायक। मैं मूल्य, सुविधाएं, सहायता आदि में आपकी मदद कर सकता हूँ। आज मैं आपकी कैसे मदद करूं?",
  mr: "👋 नमस्कार! मी PolyChat आहे, तुमचा बहुभाषिक सहाय्यक. मी किंमत, वैशिष्ट्ये, समर्थन इत्यादींमध्ये मदत करू शकतो. आज मी तुम्हाला कशी मदत करू?",
  ta: "👋 வணக்கம்! நான் PolyChat, உங்கள் பன்மொழி உதவியாளர். விலை, அம்சங்கள், ஆதரவு மற்றும் பலவற்றில் உதவ முடியும். இன்று நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?",
  pa: "👋 ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ PolyChat ਹਾਂ, ਤੁਹਾਡਾ ਬਹੁ-ਭਾਸ਼ਾਈ ਸਹਾਇਕ। ਮੈਂ ਕੀਮਤ, ਵਿਸ਼ੇਸ਼ਤਾਵਾਂ, ਸਹਾਇਤਾ ਆਦਿ ਵਿੱਚ ਤੁਹਾਡੀ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ। ਅੱਜ ਮੈਂ ਤੁਹਾਡੀ ਕਿਵੇਂ ਮਦਦ ਕਰਾਂ?",
};

const SUGGESTED_QUESTIONS: Record<Language, string[]> = {
  en: ['What are your pricing plans?', 'Do you offer a free trial?', 'How do I contact support?', 'What languages do you support?'],
  hi: ['आपकी मूल्य योजनाएं क्या हैं?', 'क्या आप निःशुल्क परीक्षण देते हैं?', 'मैं सहायता से कैसे संपर्क करूं?', 'आप किन भाषाओं का समर्थन करते हैं?'],
  mr: ['तुमच्या किंमत योजना काय आहेत?', 'तुम्ही विनामूल्य चाचणी देता का?', 'मी समर्थनाशी कसा संपर्क करू?', 'तुम्ही कोणत्या भाषांना समर्थन देता?'],
  ta: ['உங்கள் விலை திட்டங்கள் என்ன?', 'இலவச சோதனை வழங்குகிறீர்களா?', 'ஆதரவை எவ்வாறு தொடர்பு கொள்வது?', 'நீங்கள் எந்த மொழிகளை ஆதரிக்கிறீர்கள்?'],
  pa: ['ਤੁਹਾਡੀਆਂ ਕੀਮਤ ਯੋਜਨਾਵਾਂ ਕੀ ਹਨ?', 'ਕੀ ਤੁਸੀਂ ਮੁਫਤ ਅਜ਼ਮਾਇਸ਼ ਦੀ ਪੇਸ਼ਕਸ਼ ਕਰਦੇ ਹੋ?', 'ਮੈਂ ਸਹਾਇਤਾ ਨਾਲ ਕਿਵੇਂ ਸੰਪਰਕ ਕਰਾਂ?', 'ਤੁਸੀਂ ਕਿਹੜੀਆਂ ਭਾਸ਼ਾਵਾਂ ਦਾ ਸਮਰਥਨ ਕਰਦੇ ਹੋ?'],
};

export const useChatStore = create<ChatStore>()(
  persist(
    (set, get) => ({
      // Initial state
      sessionId: null,
      messages: [],
      language: 'en',
      availableLanguages: [],
      theme: 'light',
      isOpen: false,
      isLoading: false,
      isTyping: false,
      error: null,
      hasGreeted: false,

      // Initialize or restore session
      initSession: async () => {
        const { language } = get();

        // Try to restore from localStorage
        const stored = localStorage.getItem('polychat_session_id');
        if (stored) {
          set({ sessionId: stored });
          // Show greeting if no messages
          if (get().messages.length === 0) {
            const greetMsg: Message = {
              id: generateId(),
              sender: 'bot',
              text: GREETING_MESSAGES[language],
              language,
              timestamp: new Date(),
              suggested_questions: SUGGESTED_QUESTIONS[language],
            };
            set({ messages: [greetMsg], hasGreeted: true });
          }
          return;
        }

        try {
          set({ isLoading: true, error: null });
          const session = await createSession(language);
          localStorage.setItem('polychat_session_id', session.session_id);
          set({ sessionId: session.session_id });

          // Add greeting message
          const greetMsg: Message = {
            id: generateId(),
            sender: 'bot',
            text: GREETING_MESSAGES[language],
            language,
            timestamp: new Date(),
            suggested_questions: SUGGESTED_QUESTIONS[language],
          };
          set({ messages: [greetMsg], hasGreeted: true });
        } catch (err) {
          set({ error: 'Failed to start session. Please refresh the page.' });
        } finally {
          set({ isLoading: false });
        }
      },

      // Send a user message
      sendMessage: async (text: string) => {
        const { sessionId, language } = get();

        if (!sessionId) {
          await get().initSession();
        }

        const currentSessionId = get().sessionId;
        if (!currentSessionId) return;

        // Add user message immediately
        const userMsg: Message = {
          id: generateId(),
          sender: 'user',
          text,
          language,
          timestamp: new Date(),
        };

        set((state) => ({
          messages: [...state.messages, userMsg],
          isTyping: true,
          error: null,
        }));

        try {
          const response = await sendMessage({
            session_id: currentSessionId,
            message: text,
            language,
          });

          const botMsg: Message = {
            id: generateId(),
            sender: 'bot',
            text: response.answer,
            language: response.language,
            confidence: response.confidence,
            intent: response.intent,
            is_fallback: response.is_fallback,
            suggested_questions: response.suggested_questions,
            timestamp: new Date(response.timestamp),
            feedback: null,
          };

          set((state) => ({
            messages: [...state.messages, botMsg],
            isTyping: false,
          }));
        } catch (err) {
          const errorMsg: Message = {
            id: generateId(),
            sender: 'bot',
            text: '⚠️ Sorry, I encountered an error. Please try again.',
            language,
            timestamp: new Date(),
            is_fallback: true,
          };
          set((state) => ({
            messages: [...state.messages, errorMsg],
            isTyping: false,
            error: err instanceof Error ? err.message : 'Request failed',
          }));
        }
      },

      // Change language
      setLanguage: (lang: Language) => {
        set({ language: lang });
        localStorage.setItem('polychat_language', lang);
      },

      // Toggle dark/light theme
      toggleTheme: () => {
        set((state) => {
          const newTheme: Theme = state.theme === 'light' ? 'dark' : 'light';
          return { theme: newTheme };
        });
      },

      // Widget open/close
      toggleWidget: () => {
        const { isOpen } = get();
        if (!isOpen) {
          get().openWidget();
        } else {
          get().closeWidget();
        }
      },

      openWidget: () => {
        set({ isOpen: true });
        if (get().messages.length === 0) {
          get().initSession();
        }
      },

      closeWidget: () => set({ isOpen: false }),

      // Submit feedback for a message
      submitFeedback: async (messageId: string, rating: boolean) => {
        const { messages, sessionId, language } = get();
        const msg = messages.find((m) => m.id === messageId);
        if (!msg || !sessionId) return;

        // Find the user message before this bot message
        const msgIndex = messages.indexOf(msg);
        const userMsg = messages.slice(0, msgIndex).filter((m) => m.sender === 'user').pop();

        try {
          await submitFeedback({
            session_id: sessionId,
            question: userMsg?.text || '',
            answer: msg.text,
            rating,
            language,
          });

          set((state) => ({
            messages: state.messages.map((m) =>
              m.id === messageId
                ? { ...m, feedback: rating ? 'helpful' : 'not_helpful' }
                : m,
            ),
          }));
        } catch (err) {
          console.error('Failed to submit feedback:', err);
        }
      },

      // Clear error state
      clearError: () => set({ error: null }),

      // Load available languages from API
      loadLanguages: async () => {
        try {
          const data = await getLanguages();
          set({ availableLanguages: data.supported });
        } catch {
          // Use defaults if API fails
          set({
            availableLanguages: [
              { code: 'en', name: 'English', native_name: 'English', flag: '🇬🇧' },
              { code: 'hi', name: 'Hindi', native_name: 'हिंदी', flag: '🇮🇳' },
              { code: 'mr', name: 'Marathi', native_name: 'मराठी', flag: '🇮🇳' },
              { code: 'ta', name: 'Tamil', native_name: 'தமிழ்', flag: '🇮🇳' },
              { code: 'pa', name: 'Punjabi', native_name: 'ਪੰਜਾਬੀ', flag: '🇮🇳' },
            ],
          });
        }
      },
    }),
    {
      name: 'polychat-storage',
      partialize: (state) => ({
        language: state.language,
        theme: state.theme,
        sessionId: state.sessionId,
      }),
    },
  ),
);
