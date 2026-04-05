import os
from contextlib import asynccontextmanager

import faiss
import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from prompts import SOCRATES_SYSTEM_PROMPT

load_dotenv()

# ---------------------------------------------------------------------------
# Globals populated on startup
# ---------------------------------------------------------------------------
embedder: SentenceTransformer | None = None
index: faiss.IndexFlatL2 | None = None
documents: list[dict] = []
openai_client: OpenAI | None = None

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "..", "corpus", "socrates")
TOP_K = 5


# ---------------------------------------------------------------------------
# Corpus loading & indexing (adapted from RAG/RileyBrown_Cerebro_rag_guide.py)
# ---------------------------------------------------------------------------
def load_corpus(corpus_dir: str) -> list[dict]:
    """Load text files and chunk them into ~500-word segments."""
    docs = []
    doc_id = 0

    for filename in sorted(os.listdir(corpus_dir)):
        if not filename.endswith(".txt"):
            continue

        with open(os.path.join(corpus_dir, filename), "r", encoding="utf-8") as f:
            raw_text = f.read()

        paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]

        current_chunk = ""
        for para in paragraphs:
            if len((current_chunk + "\n\n" + para).split()) > 500 and current_chunk:
                docs.append({
                    "id": f"doc_{doc_id:04d}",
                    "title": filename.replace(".txt", "").replace("_", " ").title(),
                    "text": current_chunk.strip(),
                })
                doc_id += 1
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para

        if current_chunk.strip():
            docs.append({
                "id": f"doc_{doc_id:04d}",
                "title": filename.replace(".txt", "").replace("_", " ").title(),
                "text": current_chunk.strip(),
            })
            doc_id += 1

    return docs


def build_index(docs: list[dict], model: SentenceTransformer) -> faiss.IndexFlatL2:
    """Embed all document chunks and build a FAISS index."""
    texts = [doc["text"] for doc in docs]
    embeddings = model.encode(texts, show_progress_bar=True).astype("float32")
    idx = faiss.IndexFlatL2(embeddings.shape[1])
    idx.add(embeddings)
    return idx


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------
def retrieve(query: str, k: int = TOP_K) -> list[dict]:
    """Embed a query and return the top-k most similar document chunks."""
    query_vec = embedder.encode([query]).astype("float32")
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
    global embedder, index, documents, openai_client

    print("Loading embedding model...")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    print(f"Loading corpus from {CORPUS_DIR}...")
    documents = load_corpus(CORPUS_DIR)
    print(f"Loaded {len(documents)} chunks")

    print("Building FAISS index...")
    index = build_index(documents, embedder)
    print(f"Index built with {index.ntotal} vectors")

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
