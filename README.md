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

## Rebuilding the index

The FAISS index and chunk metadata (`backend/faiss_index.bin`, `backend/chunks.json`) are pre-built and committed to the repo so the server doesn't need to load any ML models at startup. If the corpus changes, rebuild them locally before deploying:

```bash
python backend/build_index.py
```

This reads `corpus/socrates/`, embeds chunks with OpenAI's `text-embedding-3-small`, and writes the two files. Requires `OPENAI_API_KEY` in `backend/.env`.

## Deployment

- **Backend** deploys to [Render](https://render.com) (Python, free tier) from the `backend/` directory.
- **Frontend** deploys to [Vercel](https://vercel.com).
- In the Vercel project settings, set the `VITE_API_URL` environment variable to the Render backend URL (e.g. `https://cerebro-api.onrender.com`). The frontend reads this at build time and points API requests at the Render backend.
- Locally, `VITE_API_URL` can be left unset — it falls back to `http://localhost:8000`, and the Vite dev server proxy still handles `/api` requests during development.

## License

All Rights Reserved (c) 2026 Riley Brown
