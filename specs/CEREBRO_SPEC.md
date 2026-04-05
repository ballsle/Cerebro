# Cerebro — Project Specification

**Author:** Riley Brown
**License:** All Rights Reserved © 2026 Riley Brown
**Version:** Alpha v0.1
**Last Updated:** April 5, 2026

---

## Overview

Cerebro is a chatbot application where users brainstorm and think through ideas by conversing with AI personas modeled after famous historical thinkers and visionaries. Each persona responds in the spirit of their real-world counterpart — adopting their philosophical frameworks, communication styles, and areas of expertise — to help users approach problems from perspectives they wouldn't normally consider.

---

## Alpha Scope (v0.1)

The alpha launches with a **single philosopher persona** to validate the core concept before expanding.

### Alpha Persona: Socrates

*(See Appendix A for other candidates considered for future releases)*

### Core Features

- **Persona Selection Screen** — For alpha, displays the single available philosopher with a brief bio. Designed to scale to a grid/list as more personas are added.
- **Chat Interface** — Standard conversational UI. User sends messages, receives responses from the selected persona.
- **Persona-Aware Responses** — The AI responds in character: adopting the philosopher's reasoning style, referencing their known works/ideas, and maintaining a consistent voice throughout the conversation.
- **Conversation Context** — The chat maintains context within a session so the philosopher can reference earlier points in the discussion.
- **New Conversation** — User can start a fresh session at any time.

### Out of Scope for Alpha

- Multiple simultaneous personas / "debate mode"
- User accounts / saved conversation history
- Voice input/output
- Mobile-native app (web-first)
- Monetization

---

## Technical Architecture

### Frontend

- **Framework:** React (single-page app)
- **Styling:** Tailwind CSS
- **Hosting:** TBD (Vercel, Netlify, or similar)

### Backend / AI

- **LLM Provider:** OpenAI API (API key provided by instructor)
- **Persona Implementation:** System prompt engineering — each philosopher has a dedicated system prompt defining their personality, reasoning style, key beliefs, historical context, and communication patterns.
- **Conversation Management:** Message history passed with each API call to maintain context within a session.

### RAG (Retrieval-Augmented Generation)

Each persona is backed by a corpus of primary source texts. When a user sends a message, relevant passages are retrieved from the corpus and included in the prompt context, grounding the persona's responses in the philosopher's actual ideas rather than relying solely on the LLM's training data.

**Socrates Corpus:**
- All 29 Plato dialogues (Jowett translations via Project Gutenberg) — including Republic, Apology, Crito, Phaedo, Meno, Symposium, Euthyphro, Gorgias, Protagoras, Phaedrus, Theaetetus, and others
- Xenophon's *Memorabilia* (4 books of Socratic conversations)
- Xenophon's *Apology* (account of Socrates' trial)
- All texts are public domain

**RAG Pipeline:**
- **Chunking Strategy:** Split by dialogue section / conversational exchange rather than arbitrary token windows, preserving the natural back-and-forth structure
- **Embedding & Retrieval:** OpenAI embeddings API (same key as the LLM) + vector DB (Chroma for local dev, or Pinecone if hosted)
- **Prompt Integration:** Retrieved passages are injected into the system prompt as reference material the persona can draw from

### System Prompt Structure (per persona)

Each persona's system prompt should include:

1. **Identity** — Who they are, when they lived, their core contributions
2. **Reasoning Style** — How they approach problems (e.g., Socratic questioning, radical skepticism, empirical analysis)
3. **Communication Style** — Tone, vocabulary, typical rhetorical devices
4. **Key Beliefs & Frameworks** — Their major philosophical positions
5. **Boundaries** — Stay in character but don't fabricate specific quotes or claim to have said things they didn't. The persona is *inspired by* the philosopher, not a historical simulation.
6. **Brainstorming Directive** — The persona's goal is to help the user think through their ideas, not just lecture. Active engagement with the user's specific problem.

---

## User Flow (Alpha)

1. User lands on the home/splash screen
2. User sees the available philosopher with a short bio card
3. User clicks to start a conversation
4. Chat interface opens — user types their idea, problem, or question
5. Philosopher persona responds in character, engaging with the user's input
6. Conversation continues until the user ends it or starts a new one

---

## Future Roadmap (Post-Alpha)

- **More personas** — Expand to 5-10 philosophers/thinkers across different traditions and eras
- **Non-Western thinkers** — Confucius, Sun Tzu, Ibn Khaldun, etc.
- **Non-philosophers** — Scientists, artists, entrepreneurs (e.g., Da Vinci, Tesla, Ada Lovelace)
- **Debate mode** — Two personas discuss the user's topic with each other
- **Persona comparison** — Ask the same question to multiple thinkers and see their different responses side by side
- **Saved sessions** — User accounts with conversation history
- **Sharing** — Export or share interesting conversations
- **Custom personas** — Let users define their own historical figure to chat with

---

## Appendix A: Alpha Persona Candidates

All candidates died over 100 years ago.

### Socrates (470–399 BC)
- **Known for:** The Socratic method (dialogue-based questioning to expose contradictions and deepen understanding), the examined life, intellectual humility ("I know that I know nothing")
- **Style:** Questions, not answers. Relentless probing. Ironic, playful, but incisive.
- **Why for alpha:** His method is inherently conversational — maps perfectly to a chatbot format. Genuinely useful as a brainstorming technique.

### René Descartes (1596–1650)
- **Known for:** Radical skepticism, "I think therefore I am," rationalism, mind-body dualism, Cartesian coordinate system
- **Style:** Methodical, systematic doubt, first-principles reasoning, building knowledge from the ground up
- **Why for alpha:** Great for users who want to break down problems systematically and question their foundational assumptions.

### Aristotle (384–322 BC)
- **Known for:** Formal logic, empiricism, the scientific method's foundations, virtue ethics, classification of knowledge across every domain
- **Style:** Encyclopedic, analytical, taxonomic — observe, categorize, reason from evidence
- **Why for alpha:** The broadest range of applicable knowledge; can engage on almost any topic.

### Friedrich Nietzsche (1844–1900)
- **Known for:** "God is dead," the Übermensch (self-overcoming), will to power, eternal recurrence, critique of conventional morality
- **Style:** Provocative, aphoristic, poetic, challenges comfortable assumptions
- **Why for alpha:** Pushes users out of conventional thinking — strong for creative and entrepreneurial brainstorming.

### Marcus Aurelius (121–180 AD)
- **Known for:** Stoicism, *Meditations*, practical wisdom on duty, self-discipline, and what's within your control
- **Style:** Grounded, pragmatic, journal-like reflections, calm under pressure
- **Why for alpha:** Strong for decision-making, leadership questions, and dealing with uncertainty.
