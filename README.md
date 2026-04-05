# Cerebro

A chatbot where users brainstorm ideas by conversing with AI personas modeled after historical philosophers. The alpha launches with Socrates.

## Setup

### Backend (Python)

```bash
cd backend
pip install -r requirements.txt
```

Create `backend/.env` with your OpenAI API key:

```
OPENAI_API_KEY=sk-your-key-here
```

### Frontend (React)

```bash
npm install
```

## Running

Open two terminals:

```bash
# Terminal 1 — Backend (loads corpus, builds FAISS index, serves API)
cd backend
uvicorn main:app --reload

# Terminal 2 — Frontend (Vite dev server, proxies /api to backend)
npm run dev
```

The frontend runs at `http://localhost:5173` and proxies `/api` requests to the backend at `http://127.0.0.1:8000`.

## How it works

1. User sends a message through the chat UI
2. Frontend sends the full conversation history to `POST /api/chat`
3. Backend embeds the latest message, retrieves relevant passages from the Socrates corpus (FAISS + sentence-transformers)
4. Backend builds a system prompt combining the Socrates persona with the retrieved context
5. Backend sends the full conversation to OpenAI (gpt-4o) and returns the response
6. Frontend displays the response in the chat

## License

All Rights Reserved (c) 2026 Riley Brown
