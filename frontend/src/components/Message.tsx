// PolyChat — Message Component (User & Bot)
import React from 'react';
import type { Message } from '@/types';
import FeedbackButtons from './FeedbackButtons';
import SuggestedQuestions from './SuggestedQuestions';

interface MessageProps {
  message: Message;
}

const formatTime = (date: Date): string => {
  return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const ConfidenceBadge: React.FC<{ confidence: number }> = ({ confidence }) => {
  const pct = Math.round(confidence * 100);
  const color =
    pct >= 90
      ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
      : pct >= 75
        ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
        : pct >= 60
          ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
          : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400';

  return (
    <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${color}`}>
      {pct}% match
    </span>
  );
};

const MessageBubble: React.FC<MessageProps> = ({ message }) => {
  const isUser = message.sender === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end mb-3 animate-fade-in">
        <div className="max-w-[80%]">
          <div className="bg-blue-600 text-white rounded-2xl rounded-br-sm px-4 py-3 shadow-sm">
            <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">
              {message.text}
            </p>
          </div>
          <div className="text-right mt-1">
            <span className="text-[10px] text-gray-400 dark:text-gray-500">
              {formatTime(message.timestamp)}
            </span>
          </div>
        </div>
      </div>
    );
  }

  // Helper to parse simple markdown bold formatting (**text**)
  const renderFormattedText = (text: string) => {
    if (!text) return null;
    const parts = text.split(/\*\*([^*]+)\*\*/g);
    return parts.map((part, index) => {
      if (index % 2 === 1) {
        return <strong key={index} className="font-bold text-gray-950 dark:text-white">{part}</strong>;
      }
      return part;
    });
  };

  // Bot message
  return (
    <div className="flex items-end gap-2 mb-3 animate-fade-in">
      {/* Bot avatar */}
      <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0 text-white text-xs font-bold shadow-sm">
        P
      </div>

      <div className="max-w-[85%]">
        <div className="bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
          {/* Message text */}
          <p className="text-sm leading-relaxed text-gray-800 dark:text-gray-100 whitespace-pre-wrap break-words">
            {renderFormattedText(message.text)}
          </p>

          {/* Suggested questions */}
          {message.suggested_questions && message.suggested_questions.length > 0 && (
            <SuggestedQuestions questions={message.suggested_questions} />
          )}

          {/* Feedback buttons (only for bot messages) */}
          {!message.is_fallback && (
            <FeedbackButtons message={message} />
          )}
        </div>

        {/* Meta info */}
        <div className="flex items-center gap-2 mt-1">
          <span className="text-[10px] text-gray-400 dark:text-gray-500">
            {formatTime(message.timestamp)}
          </span>
          {message.confidence !== undefined && !message.is_fallback && (
            <ConfidenceBadge confidence={message.confidence} />
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
