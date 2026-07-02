// PolyChat — ChatWidget Component (Main Container)
import React, { useEffect } from 'react';
import { useChatStore } from '@/store/chatStore';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import LanguageSelector from './LanguageSelector';

const ChatWidget: React.FC = () => {
  const {
    isOpen,
    toggleWidget,
    closeWidget,
    theme,
    toggleTheme,
    loadLanguages,
    error,
    clearError,
  } = useChatStore();

  // Fetch languages on mount
  useEffect(() => {
    void loadLanguages();
  }, [loadLanguages]);

  // Apply theme to body
  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col items-end font-sans">
      {/* Expanded Chat Window */}
      {isOpen && (
        <div className="bg-gray-50 dark:bg-gray-900 w-[350px] sm:w-[380px] h-[550px] max-h-[calc(100vh-100px)] rounded-2xl shadow-2xl flex flex-col mb-4 border border-gray-200 dark:border-gray-700 overflow-hidden animate-slide-up transform origin-bottom-right">
          
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-3 flex items-center justify-between shadow-md relative z-10">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-white/20 flex items-center justify-center text-white font-bold text-lg border border-white/30 shadow-inner">
                P
              </div>
              <div>
                <h3 className="text-white font-semibold text-[15px] leading-tight">PolyChat</h3>
                <p className="text-blue-100 text-[11px] font-medium flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-400"></span> Online
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <LanguageSelector />
              
              <button
                onClick={toggleTheme}
                className="w-7 h-7 rounded-full bg-white/10 hover:bg-white/25 flex items-center justify-center text-white transition-colors"
                aria-label="Toggle theme"
                title={theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
              >
                {theme === 'dark' ? '☀️' : '🌙'}
              </button>
              
              <button
                onClick={closeWidget}
                className="w-7 h-7 rounded-full bg-white/10 hover:bg-white/25 flex items-center justify-center text-white transition-colors cursor-pointer"
                aria-label="Close widget"
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
                  <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
                </svg>
              </button>
            </div>
          </div>

          {/* Error banner */}
          {error && (
            <div className="bg-red-500 text-white px-3 py-2 text-xs flex items-center justify-between">
              <span>{error}</span>
              <button onClick={clearError} className="hover:text-red-200">✕</button>
            </div>
          )}

          {/* Scrollable Message Area */}
          <MessageList />

          {/* Input Area */}
          <ChatInput />
        </div>
      )}

      {/* Floating Action Button (FAB) */}
      <button
        onClick={toggleWidget}
        className={`
          flex items-center justify-center rounded-full shadow-xl transition-all duration-300 z-50 cursor-pointer hover:scale-105
          ${isOpen 
            ? 'w-12 h-12 bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300' 
            : 'w-14 h-14 bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:shadow-blue-500/30'}
        `}
        aria-label={isOpen ? 'Close Chat' : 'Open Chat'}
      >
        {isOpen ? (
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
            <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
          </svg>
        ) : (
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-7 h-7">
            <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 9.75a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375m-13.5 3.01c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.184-4.183a1.14 1.14 0 01.778-.332 48.294 48.294 0 005.83-.498c1.585-.233 2.708-1.626 2.708-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" />
          </svg>
        )}
      </button>
    </div>
  );
};

export default ChatWidget;
