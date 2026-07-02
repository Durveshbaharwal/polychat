// PolyChat — SuggestedQuestions Component
import React from 'react';
import { useChatStore } from '@/store/chatStore';

interface SuggestedQuestionsProps {
  questions: string[];
}

const SuggestedQuestions: React.FC<SuggestedQuestionsProps> = ({ questions }) => {
  const sendMessage = useChatStore((s) => s.sendMessage);

  if (!questions || questions.length === 0) return null;

  return (
    <div className="mt-3 flex flex-wrap gap-2">
      {questions.map((q, i) => (
        <button
          key={i}
          onClick={() => void sendMessage(q)}
          className="text-xs bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-300 border border-blue-200 dark:border-blue-700 rounded-full px-3 py-1.5 hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors cursor-pointer text-left"
          aria-label={`Ask: ${q}`}
        >
          {q}
        </button>
      ))}
    </div>
  );
};

export default SuggestedQuestions;
