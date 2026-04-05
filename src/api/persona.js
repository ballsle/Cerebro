/**
 * Send conversation history to the backend and get the persona's response.
 * The backend handles RAG retrieval, system prompt building, and OpenAI calls.
 */
export async function getPersonaResponse(persona, messages) {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    const msg = body?.detail || `Server error (${res.status})`;
    throw new Error(msg);
  }

  const data = await res.json();
  return data.reply;
}
