import { useState } from 'react';

export default function ChatInput({ onSend, disabled }) {
  const [text, setText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText('');
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex items-center gap-2 px-4 py-3 border-t border-surface-600"
    >
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Type your message..."
        className="flex-1 bg-surface-700 border border-surface-600 rounded-lg px-4 py-2.5 text-sm text-zinc-200 placeholder-zinc-500 outline-none focus:border-navy-500/40 transition-colors"
      />
      <button
        type="submit"
        disabled={disabled}
        className="px-4 py-2.5 rounded-lg bg-navy-500/15 border border-navy-500/25 text-navy-400 text-sm font-medium hover:bg-navy-500/25 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
      >
        Send
      </button>
    </form>
  );
}
