// PolyChat — FeedbackButtons Component
import React from 'react';
import type { Message } from '@/types';
import { useChatStore } from '@/store/chatStore';

interface FeedbackButtonsProps {
  message: Message;
}

const FeedbackButtons: React.FC<FeedbackButtonsProps> = ({ message }) => {
  const submitFeedback = useChatStore((s) => s.submitFeedback);

  if (message.feedback !== null && message.feedback !== undefined) {
    return (
      <div className="mt-2 text-xs text-gray-400 dark:text-gray-500">
        {message.feedback === 'helpful' ? '✅ Thanks for the feedback!' : '📝 We\'ll work on improving this.'}
      </div>
    );
  }

  return (
    <div className="mt-2 flex items-center gap-2">
      <span className="text-xs text-gray-400 dark:text-gray-500">Was this helpful?</span>
      <button
        onClick={() => void submitFeedback(message.id, true)}
        className="text-base hover:scale-125 transition-transform cursor-pointer"
        aria-label="Helpful"
        title="Helpful"
      >
        👍
      </button>
      <button
        onClick={() => void submitFeedback(message.id, false)}
        className="text-base hover:scale-125 transition-transform cursor-pointer"
        aria-label="Not helpful"
        title="Not helpful"
      >
        👎
      </button>
    </div>
  );
};

export default FeedbackButtons;
