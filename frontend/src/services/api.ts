// PolyChat — Axios API Service

import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  ChatRequest,
  ChatResponse,
  FeedbackRequest,
  LanguagesResponse,
  SessionCreateResponse,
  Language,
} from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

// ── Request interceptor: inject session ID ────────────────────────────────────
apiClient.interceptors.request.use((config) => {
  const sessionId = localStorage.getItem('polychat_session_id');
  if (sessionId) {
    config.headers['X-Session-ID'] = sessionId;
  }
  return config;
});

// ── Response interceptor: normalize errors ────────────────────────────────────
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response) {
      const data = error.response.data as { error?: { message?: string } };
      const message = data?.error?.message || 'An error occurred. Please try again.';
      return Promise.reject(new Error(message));
    }
    if (error.request) {
      return Promise.reject(new Error('Network error. Please check your connection.'));
    }
    return Promise.reject(error);
  },
);

// ── API Functions ─────────────────────────────────────────────────────────────

export const createSession = async (language: Language = 'en'): Promise<SessionCreateResponse> => {
  const response = await apiClient.post<SessionCreateResponse>(
    `/session?language=${language}`,
  );
  return response.data;
};

export const deleteSession = async (sessionId: string): Promise<void> => {
  await apiClient.delete(`/session?session_id=${sessionId}`);
};

export const sendMessage = async (request: ChatRequest): Promise<ChatResponse> => {
  const response = await apiClient.post<ChatResponse>('/chat', request);
  return response.data;
};

export const submitFeedback = async (request: FeedbackRequest): Promise<void> => {
  await apiClient.post('/feedback', request);
};

export const getLanguages = async (): Promise<LanguagesResponse> => {
  const response = await apiClient.get<LanguagesResponse>('/languages');
  return response.data;
};

export const checkHealth = async (): Promise<{ status: string }> => {
  const response = await apiClient.get<{ status: string }>('/health');
  return response.data;
};

export default apiClient;
