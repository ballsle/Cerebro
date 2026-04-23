export default function PersonaCard({ persona, onSelect }) {
  return (
    <div className="w-80 bg-surface-800 border border-surface-600 rounded-lg p-6 hover:border-navy-500/40 transition-colors group flex flex-col">
      {/* Icon */}
      <div className="w-16 h-16 rounded-full bg-surface-700 border border-surface-600 flex items-center justify-center mb-4 mx-auto group-hover:border-navy-500/30 transition-colors">
        <span className="text-2xl font-serif font-semibold text-navy-400">
          {persona.name[0]}
        </span>
      </div>

      {/* Info */}
      <div className="text-center mb-5 flex-1">
        <h3 className="text-xl font-serif font-semibold text-zinc-100 mb-1">
          {persona.name}
        </h3>
        <p className="text-xs text-navy-500/70 tracking-wider uppercase mb-3">
          {persona.dates}
        </p>
        <p className="text-sm text-zinc-400 leading-relaxed">
          {persona.bio}
        </p>
      </div>

      {/* CTA */}
      <button
        onClick={onSelect}
        className="w-full py-2.5 rounded bg-navy-500/10 border border-navy-500/20 text-navy-400 text-sm font-medium hover:bg-navy-500/20 hover:border-navy-500/40 transition-colors"
      >
        Start Conversation
      </button>
    </div>
  );
}
