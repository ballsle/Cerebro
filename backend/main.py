import json
import os
from contextlib import asynccontextmanager

import faiss
import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel

from prompts import SOCRATES_SYSTEM_PROMPT

load_dotenv()

# ---------------------------------------------------------------------------
# Globals populated on startup
# ---------------------------------------------------------------------------
index: faiss.IndexFlatL2 | None = None
documents: list[dict] = []
openai_client: OpenAI | None = None

INDEX_PATH = os.path.join(os.path.dirname(__file__), "faiss_index.bin")
CHUNKS_PATH = os.path.join(os.path.dirname(__file__), "chunks.json")
EMBED_MODEL = "text-embedding-3-small"
TOP_K = 5


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------
def embed_query(query: str) -> np.ndarray:
    """Embed a query using OpenAI's embedding API."""
    resp = openai_client.embeddings.create(model=EMBED_MODEL, input=[query])
    return np.array([resp.data[0].embedding], dtype="float32")


def retrieve(query: str, k: int = TOP_K) -> list[dict]:
    """Embed a query and return the top-k most similar document chunks."""
    query_vec = embed_query(query)
    distances, indices = index.search(query_vec, k)
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        doc = documents[idx].copy()
        doc["score"] = float(dist)
        results.append(doc)
    return results


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------
def build_system_prompt(chunks: list[dict]) -> str:
    """Combine the Socrates persona prompt with retrieved context."""
    context_block = "\n\n".join(
        f"[{c['title']}]\n{c['text']}" for c in chunks
    )
    return (
        f"{SOCRATES_SYSTEM_PROMPT}\n\n"
        f"## Reference Material\n"
        f"Use the following passages from dialogues about your life and teachings "
        f"to ground your responses. Draw on this context when relevant, but do not "
        f"fabricate specific quotes or claim to have said things not found here.\n\n"
        f"=== CONTEXT ===\n{context_block}\n=== END CONTEXT ==="
    )


# ---------------------------------------------------------------------------
# App lifecycle
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    global index, documents, openai_client

    print(f"Loading FAISS index from {INDEX_PATH}...")
    index = faiss.read_index(INDEX_PATH)
    print(f"Index loaded with {index.ntotal} vectors")

    print(f"Loading chunks from {CHUNKS_PATH}...")
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        documents = json.load(f)
    print(f"Loaded {len(documents)} chunks")

    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    yield


app = FastAPI(title="Cerebro API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------
class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


class ChatResponse(BaseModel):
    reply: str


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------
@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages array is empty")

    latest_user_msg = req.messages[-1].content

    # Retrieve relevant chunks
    chunks = retrieve(latest_user_msg, k=TOP_K)

    # Build system prompt with RAG context
    system_prompt = build_system_prompt(chunks)

    # Assemble messages for OpenAI
    openai_messages = [{"role": "system", "content": system_prompt}]
    for msg in req.messages:
        openai_messages.append({"role": msg.role, "content": msg.content})

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=openai_messages,
            temperature=0.8,
            max_tokens=1024,
        )
        reply = response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return ChatResponse(reply=reply)
