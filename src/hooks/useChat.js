import { useState, useCallback } from 'react';
import { getPersonaResponse } from '../api/persona';

export default function useChat(persona) {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendMessage = useCallback(
    async (content) => {
      const userMsg = { role: 'user', content };
      setMessages((prev) => [...prev, userMsg]);
      setError(null);
      setIsLoading(true);

      try {
        const updatedHistory = [...messages, userMsg];
        const reply = await getPersonaResponse(persona, updatedHistory);
        setMessages((prev) => [...prev, { role: 'assistant', content: reply }]);
      } catch (err) {
        setError(err.message || 'Something went wrong. Please try again.');
      } finally {
        setIsLoading(false);
      }
    },
    [messages, persona]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  const dismissError = useCallback(() => setError(null), []);

  return { messages, isLoading, error, sendMessage, clearMessages, dismissError };
}
