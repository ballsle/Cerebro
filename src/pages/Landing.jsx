import PersonaCard from '../components/PersonaCard';

const personas = [
  {
    id: 'socrates',
    name: 'Socrates',
    dates: '470–399 BC',
    bio: 'The father of Western philosophy, known for the Socratic method of questioning',
  },
];

export default function Landing({ onSelectPersona }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-4">
      <div className="text-center mb-12">
        <h1 className="text-5xl font-serif font-semibold text-navy-400 tracking-wide mb-3">
          Cerebro
        </h1>
        <p className="text-zinc-400 text-lg max-w-md mx-auto">
          Brainstorm with history's greatest thinkers
        </p>
      </div>

      <div className="flex flex-wrap justify-center gap-6">
        {personas.map((persona) => (
          <PersonaCard
            key={persona.id}
            persona={persona}
            onSelect={() => onSelectPersona(persona)}
          />
        ))}
      </div>
    </div>
  );
}
