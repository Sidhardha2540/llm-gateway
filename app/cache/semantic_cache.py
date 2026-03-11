"""
Semantic cache: embed prompt, cosine similarity with stored entries, return cached response if match.
Uses OpenAI embeddings and Redis for storage.
"""
import json
import uuid
import numpy as np
from typing import Any, Optional

from app.cache.redis_client import get_redis, set_json, get_json
from app.providers.openai_provider import get_embedding

# Key prefix and list key for semantic entries
SEMANTIC_PREFIX = "llm_gateway:semantic:"
SEMANTIC_INDEX_KEY = "llm_gateway:semantic_index"
MAX_CACHE_ENTRIES = 500
SIMILARITY_THRESHOLD = 0.95


def cosine_similarity(a: list[float], b: list[float]) -> float:
    va, vb = np.array(a, dtype=float), np.array(b, dtype=float)
    return float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb) + 1e-9))


async def _get_index() -> list[dict]:
    r = await get_redis()
    raw = await r.get(SEMANTIC_INDEX_KEY)
    if not raw:
        return []
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


async def _set_index(entries: list[dict], max_entries: int = MAX_CACHE_ENTRIES) -> None:
    if len(entries) > max_entries:
        entries = entries[-max_entries:]
    r = await get_redis()
    await r.set(SEMANTIC_INDEX_KEY, json.dumps(entries), ex=86400 * 7)  # 7 days


async def get_cached_response(prompt_text: str) -> Optional[dict[str, Any]]:
    """
    Embed prompt, compare to stored embeddings; if similarity >= threshold, return cached response.
    """
    try:
        query_embedding = await get_embedding(prompt_text)
    except Exception:
        return None

    index = await _get_index()
    if not index:
        return None

    best_score = 0.0
    best_id = None
    for entry in index:
        emb = entry.get("embedding")
        if not emb:
            continue
        sim = cosine_similarity(query_embedding, emb)
        if sim >= SIMILARITY_THRESHOLD and sim > best_score:
            best_score = sim
            best_id = entry.get("response_id")

    if best_id is None:
        return None

    cached = await get_json(f"{SEMANTIC_PREFIX}resp:{best_id}")
    return cached


async def set_cached_response(prompt_text: str, response: dict[str, Any], ttl_seconds: int = 3600) -> None:
    """
    Embed prompt, store embedding + response in Redis, append to index.
    """
    try:
        embedding = await get_embedding(prompt_text)
    except Exception:
        return

    response_id = str(uuid.uuid4())
    await set_json(f"{SEMANTIC_PREFIX}resp:{response_id}", response, ttl_seconds=ttl_seconds)

    index = await _get_index()
    index.append({"response_id": response_id, "embedding": embedding})
    await _set_index(index)
