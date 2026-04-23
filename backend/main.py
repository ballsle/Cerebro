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

from prompts import PERSONA_PROMPTS

load_dotenv()

BACKEND_DIR = os.path.dirname(__file__)
EMBED_MODEL = "text-embedding-3-small"
TOP_K = 5

# Populated on startup: { philosopher_id: { "index": faiss index, "documents": [...] } }
persona_data: dict[str, dict] = {}
openai_client: OpenAI | None = None

PHILOSOPHERS = ["socrates", "aristotle", "chomsky"]


def _load_persona(philosopher: str) -> dict | None:
    index_path = os.path.join(BACKEND_DIR, f"faiss_index_{philosopher}.bin")
    chunks_path = os.path.join(BACKEND_DIR, f"chunks_{philosopher}.json")

    if not os.path.exists(index_path) or not os.path.exists(chunks_path):
        print(f"  WARNING: index files not found for '{philosopher}', skipping")
        return None

    index = faiss.read_index(index_path)
    with open(chunks_path, "r", encoding="utf-8") as f:
        documents = json.load(f)

    print(f"  Loaded {philosopher}: {index.ntotal} vectors, {len(documents)} chunks")
    return {"index": index, "documents": documents}


def embed_query(query: str) -> np.ndarray:
    resp = openai_client.embeddings.create(model=EMBED_MODEL, input=[query])
    return np.array([resp.data[0].embedding], dtype="float32")


def retrieve(philosopher: str, query: str, k: int = TOP_K) -> list[dict]:
    data = persona_data[philosopher]
    query_vec = embed_query(query)
    distances, indices = data["index"].search(query_vec, k)
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        doc = data["documents"][idx].copy()
        doc["score"] = float(dist)
        results.append(doc)
    return results


def build_system_prompt(philosopher: str, chunks: list[dict]) -> str:
    persona_prompt = PERSONA_PROMPTS[philosopher]
    context_block = "\n\n".join(
        f"[{c['title']}]\n{c['text']}" for c in chunks
    )
    return (
        f"{persona_prompt}\n\n"
        f"## Reference Material\n"
        f"Use the following passages from source texts to ground your responses. "
        f"Draw on this context when relevant, but do not fabricate specific quotes "
        f"or claim to have said things not found here.\n\n"
        f"=== CONTEXT ===\n{context_block}\n=== END CONTEXT ==="
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    global openai_client

    print("Loading persona indexes...")
    for philosopher in PHILOSOPHERS:
        data = _load_persona(philosopher)
        if data:
            persona_data[philosopher] = data

    if not persona_data:
        raise RuntimeError("No persona indexes found. Run build_index.py for at least one philosopher.")

    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    print(f"Ready. Loaded personas: {list(persona_data.keys())}")
    yield


app = FastAPI(title="Cerebro API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    persona: str
    messages: list[Message]


class ChatResponse(BaseModel):
    reply: str


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages array is empty")

    if req.persona not in persona_data:
        available = list(persona_data.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Unknown persona '{req.persona}'. Available: {available}",
        )

    latest_user_msg = req.messages[-1].content
    chunks = retrieve(req.persona, latest_user_msg, k=TOP_K)
    system_prompt = build_system_prompt(req.persona, chunks)

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
