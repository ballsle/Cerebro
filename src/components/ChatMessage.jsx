export default function ChatMessage({ message, personaName }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex animate-message-in ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? 'bg-surface-600 text-zinc-200'
            : 'bg-surface-700 border border-surface-600 text-zinc-300'
        }`}
      >
        {!isUser && (
          <span className="block text-xs text-navy-500/70 font-serif mb-1">
            {personaName}
          </span>
        )}
        {message.content}
      </div>
    </div>
  );
}
