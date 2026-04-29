import os
from functools import lru_cache

from app.config.settings import (
    EMBEDDING_MODEL,
    PINECONE_API_KEY,
    PINECONE_INDEX,
    PINECONE_NAMESPACE,
    require_setting,
)


@lru_cache
def get_embedding_model():
    """Load the fastembed ONNX model once and cache it.

    fastembed uses ONNX Runtime (no PyTorch) so RAM usage is ~100 MB,
    comfortably within Render's free-tier 512 MB limit.
    """
    from fastembed import TextEmbedding
    return TextEmbedding(model_name=f"sentence-transformers/{EMBEDDING_MODEL}")


def get_embedding(text: str) -> list:
    """Get embedding using fastembed (ONNX-based, memory-efficient)."""
    model = get_embedding_model()
    # embed() returns a generator; we take the first (and only) result
    embeddings = list(model.embed([text]))
    return embeddings[0].tolist()


@lru_cache
def get_index():
    from pinecone import Pinecone

    pc = Pinecone(api_key=require_setting("PINECONE_API_KEY", PINECONE_API_KEY))
    return pc.Index(require_setting("PINECONE_INDEX", PINECONE_INDEX))


def retrieve(query: str, top_k: int = 5):
    index = get_index()
    query_embedding = get_embedding(query)

    query_args = {
        "vector": query_embedding,
        "top_k": top_k,
        "include_metadata": True,
    }
    if PINECONE_NAMESPACE:
        query_args["namespace"] = PINECONE_NAMESPACE

    results = index.query(**query_args)

    matches = getattr(results, "matches", None)
    if matches is None:
        matches = results.get("matches", [])

    contexts = []
    seen = set()
    for match in matches:
        metadata = getattr(match, "metadata", None)
        if metadata is None:
            metadata = match.get("metadata") or {}
        text = metadata.get("text")
        if text and text not in seen:
            contexts.append(text)
            seen.add(text)
    return contexts
