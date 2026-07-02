// PolyChat — ChatInput Component
import React, { useState, useRef, useEffect } from 'react';
import { useChatStore } from '@/store/chatStore';

const ChatInput: React.FC = () => {
  const [text, setText] = useState('');
  const { sendMessage, isTyping } = useChatStore();
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 120)}px`;
    }
  }, [text]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || isTyping) return;

    void sendMessage(trimmed);
    setText('');
    
    // Reset height
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="p-3 bg-white dark:bg-gray-800 border-t border-gray-100 dark:border-gray-700">
      <form
        onSubmit={handleSubmit}
        className="flex items-end gap-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-2xl p-1 shadow-inner focus-within:ring-2 focus-within:ring-blue-500/20 focus-within:border-blue-400 transition-all"
      >
        <textarea
          ref={inputRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your question..."
          className="flex-1 max-h-[120px] bg-transparent text-sm text-gray-800 dark:text-gray-100 placeholder-gray-400 border-none outline-none resize-none py-2.5 px-3 scrollbar-thin"
          rows={1}
          disabled={isTyping}
        />
        <button
          type="submit"
          disabled={!text.trim() || isTyping}
          className="w-10 h-10 flex-shrink-0 flex items-center justify-center rounded-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 dark:disabled:bg-gray-700 disabled:cursor-not-allowed text-white transition-colors cursor-pointer mb-0.5 mr-0.5"
          aria-label="Send message"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
            className="w-5 h-5 -mr-1"
          >
            <path d="M3.478 2.404a.75.75 0 00-.926.941l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.404z" />
          </svg>
        </button>
      </form>
      
      {/* Branding footer */}
      <div className="text-center mt-2">
        <a href="https://polychat.ai" target="_blank" rel="noopener noreferrer" className="text-[10px] text-gray-400 dark:text-gray-500 hover:text-gray-500 dark:hover:text-gray-400 transition-colors inline-flex items-center gap-1 font-medium">
          Powered by <span className="text-blue-500 font-semibold tracking-wide">PolyChat</span>
        </a>
      </div>
    </div>
  );
};

export default ChatInput;
