from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from pathlib import Path
import json
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config.settings import (
    EMBEDDING_MODEL,
    PINECONE_API_KEY,
    PINECONE_INDEX,
    PINECONE_NAMESPACE,
    require_setting,
)

PROCESSED_PATH = ROOT_DIR / "data" / "processed" / "faqs.jsonl"
BATCH_SIZE = 100


def batched(items, size):
    for start in range(0, len(items), size):
        yield items[start:start + size]


def main():
    if not PROCESSED_PATH.exists():
        raise FileNotFoundError(f"Run scripts/preprocess.py first. Missing: {PROCESSED_PATH}")

    with PROCESSED_PATH.open("r", encoding="utf-8") as file:
        records = [json.loads(line) for line in file]

    model = SentenceTransformer(EMBEDDING_MODEL)
    pc = Pinecone(api_key=require_setting("PINECONE_API_KEY", PINECONE_API_KEY))
    index = pc.Index(require_setting("PINECONE_INDEX", PINECONE_INDEX))

    uploaded = 0
    for batch in batched(records, BATCH_SIZE):
        texts = [item["text"] for item in batch]
        embeddings = model.encode(texts).tolist()
        vectors = []

        for item, embedding in zip(batch, embeddings):
            vectors.append(
                {
                    "id": item["id"],
                    "values": embedding,
                    "metadata": {
                        "text": item["text"],
                        "question": item["question"],
                        "answer": item["answer"],
                        "source": item["source"],
                    },
                }
            )

        if PINECONE_NAMESPACE:
            index.upsert(vectors=vectors, namespace=PINECONE_NAMESPACE)
        else:
            index.upsert(vectors=vectors)
        uploaded += len(vectors)
        print(f"Uploaded {uploaded}/{len(records)}")

    print("Pinecone upload complete.")


if __name__ == "__main__":
    main()
