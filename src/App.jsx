import { useState } from 'react';
import Landing from './pages/Landing';
import Chat from './pages/Chat';

export default function App() {
  const [activePersona, setActivePersona] = useState(null);

  return (
    <div className="min-h-screen bg-surface-900">
      {activePersona ? (
        <Chat
          persona={activePersona}
          onExit={() => setActivePersona(null)}
        />
      ) : (
        <Landing onSelectPersona={setActivePersona} />
      )}
    </div>
  );
}
