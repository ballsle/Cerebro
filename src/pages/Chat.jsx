import { useRef, useEffect } from 'react';
import useChat from '../hooks/useChat';
import ChatMessage from '../components/ChatMessage';
import ChatInput from '../components/ChatInput';

export default function Chat({ persona, onExit }) {
  const { messages, isLoading, error, sendMessage, clearMessages, dismissError } = useChat(persona);
  const scrollRef = useRef(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex flex-col h-screen max-w-3xl mx-auto animate-fade-in">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 border-b border-surface-600">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-surface-600 flex items-center justify-center text-navy-400 font-serif text-sm font-semibold">
            {persona.name[0]}
          </div>
          <div>
            <h2 className="text-sm font-medium text-zinc-200">{persona.name}</h2>
            <p className="text-xs text-zinc-500">{persona.dates}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={clearMessages}
            className="text-xs text-zinc-400 hover:text-zinc-200 px-3 py-1.5 rounded border border-surface-600 hover:border-zinc-500 transition-colors"
          >
            New Conversation
          </button>
          <button
            onClick={onExit}
            className="text-xs text-zinc-400 hover:text-zinc-200 px-3 py-1.5 rounded border border-surface-600 hover:border-zinc-500 transition-colors"
          >
            Back
          </button>
        </div>
      </header>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto chat-scroll px-4 py-6 space-y-4">
        {messages.length === 0 && !isLoading && (
          <div className="flex items-center justify-center h-full">
            <p className="text-zinc-600 text-2xl italic font-serif">
              Begin your dialogue with {persona.name}...
            </p>
          </div>
        )}
        {messages.map((msg, i) => (
          <ChatMessage key={i} message={msg} personaName={persona.name} />
        ))}
        {isLoading && (
          <div className="flex justify-start animate-message-in">
            <div className="bg-surface-700 border border-surface-600 rounded-lg px-4 py-3">
              <span className="block text-xs text-navy-500/70 font-serif mb-1">{persona.name}</span>
              <span className="flex items-center gap-1 py-1">
                <span className="typing-dot w-1.5 h-1.5 rounded-full bg-zinc-400" />
                <span className="typing-dot w-1.5 h-1.5 rounded-full bg-zinc-400" />
                <span className="typing-dot w-1.5 h-1.5 rounded-full bg-zinc-400" />
              </span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Error */}
      {error && (
        <div className="mx-4 mb-2 px-4 py-2 rounded bg-red-900/30 border border-red-800/40 text-red-300 text-sm flex items-center justify-between">
          <span>{error}</span>
          <button onClick={dismissError} className="text-red-400 hover:text-red-200 ml-3 text-xs">
            Dismiss
          </button>
        </div>
      )}

      {/* Input */}
      <ChatInput onSend={sendMessage} disabled={isLoading} />
    </div>
  );
}
