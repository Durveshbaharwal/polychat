// PolyChat — TypeScript Type Definitions

export type Language = 'en' | 'hi' | 'mr' | 'ta' | 'pa';

export interface LanguageInfo {
  code: Language;
  name: string;
  native_name: string;
  flag: string;
}

export type MessageSender = 'user' | 'bot';

export interface Message {
  id: string;
  sender: MessageSender;
  text: string;
  language: Language;
  confidence?: number;
  intent?: string;
  is_fallback?: boolean;
  suggested_questions?: string[];
  timestamp: Date;
  feedback?: 'helpful' | 'not_helpful' | null;
  faq_id?: string;
}

export interface ChatRequest {
  session_id: string;
  message: string;
  language?: Language;
}

export interface ChatResponse {
  session_id: string;
  message: string;
  answer: string;
  language: Language;
  detected_language: Language;
  intent?: string;
  confidence: number;
  is_fallback: boolean;
  suggested_questions: string[];
  timestamp: string;
}

export interface FeedbackRequest {
  session_id: string;
  faq_id?: string;
  question: string;
  answer: string;
  rating: boolean;
  language: Language;
  comment?: string;
}

export interface SessionCreateResponse {
  session_id: string;
  language: Language;
  created_at: string;
}

export interface HealthResponse {
  status: 'ok' | 'degraded' | 'error';
  version: string;
  environment: string;
  components: Record<string, { status: string; message?: string }>;
  timestamp: string;
}

export interface LanguagesResponse {
  supported: LanguageInfo[];
  default: Language;
}

export type Theme = 'light' | 'dark';

export interface WidgetConfig {
  apiBaseUrl: string;
  defaultLanguage: Language;
  theme: Theme;
  title: string;
  subtitle: string;
  placeholder: string;
}
