"""
Pre-build the FAISS index and chunk metadata locally.

Run this whenever the corpus changes:
    python backend/build_index.py

It produces two files committed to the repo and shipped to the server:
    backend/faiss_index.bin   - FAISS index of chunk embeddings
    backend/chunks.json       - chunk text + title metadata (parallel to index)

Embeddings use OpenAI's text-embedding-3-small so the server can embed
queries with the same model at request time without loading a local model.
"""
import json
import os

import faiss
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "..", "corpus", "socrates")
INDEX_PATH = os.path.join(os.path.dirname(__file__), "faiss_index.bin")
CHUNKS_PATH = os.path.join(os.path.dirname(__file__), "chunks.json")

EMBED_MODEL = "text-embedding-3-small"
EMBED_BATCH = 100


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


def embed_texts(client: OpenAI, texts: list[str]) -> np.ndarray:
    """Embed texts with OpenAI in batches and return a float32 matrix."""
    vectors: list[list[float]] = []
    for i in range(0, len(texts), EMBED_BATCH):
        batch = texts[i : i + EMBED_BATCH]
        resp = client.embeddings.create(model=EMBED_MODEL, input=batch)
        vectors.extend(item.embedding for item in resp.data)
        print(f"  embedded {min(i + EMBED_BATCH, len(texts))}/{len(texts)}")
    return np.array(vectors, dtype="float32")


def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY not set (check backend/.env)")

    client = OpenAI(api_key=api_key)

    print(f"Loading corpus from {CORPUS_DIR}...")
    documents = load_corpus(CORPUS_DIR)
    print(f"Loaded {len(documents)} chunks")

    print(f"Embedding with {EMBED_MODEL}...")
    embeddings = embed_texts(client, [d["text"] for d in documents])

    print(f"Building FAISS index ({embeddings.shape[1]} dims)...")
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    print(f"Writing {INDEX_PATH}")
    faiss.write_index(index, INDEX_PATH)

    print(f"Writing {CHUNKS_PATH}")
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)

    print(f"Done. {len(documents)} chunks indexed.")


if __name__ == "__main__":
    main()
