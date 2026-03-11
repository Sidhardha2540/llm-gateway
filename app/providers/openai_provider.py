"""
OpenAI API client: chat completion and streaming.
"""
import os
import time
from typing import Any, AsyncIterator, Optional
from openai import AsyncOpenAI

_client: Optional[AsyncOpenAI] = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY not set")
        _client = AsyncOpenAI(api_key=key)
    return _client


def openai_model_to_provider(model: str) -> str:
    if model.startswith("gpt-"):
        return "openai"
    return "openai"


# Approximate cost per 1K tokens (USD) for common models
OPENAI_COST = {
    "gpt-4": (0.03, 0.06),
    "gpt-4-turbo": (0.01, 0.03),
    "gpt-4o": (0.005, 0.015),
    "gpt-3.5-turbo": (0.0005, 0.0015),
}


def estimate_cost_openai(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    in_cost, out_cost = OPENAI_COST.get(model, (0.01, 0.03))
    return (prompt_tokens / 1000 * in_cost) + (completion_tokens / 1000 * out_cost)


async def chat_completion(
    model: str,
    messages: list[dict[str, Any]],
    stream: bool = False,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    timeout: float = 60.0,
) -> dict[str, Any] | AsyncIterator[Any]:
    client = get_client()
    kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": stream,
        "timeout": timeout,
    }
    if temperature is not None:
        kwargs["temperature"] = temperature
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens

    start = time.perf_counter()
    if stream:
        return client.chat.completions.create(**kwargs)
    resp = await client.chat.completions.create(**kwargs)
    latency_ms = int((time.perf_counter() - start) * 1000)
    # Attach latency for audit
    setattr(resp, "_latency_ms", latency_ms)
    return resp


async def get_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    client = get_client()
    resp = await client.embeddings.create(input=text, model=model)
    return resp.data[0].embedding
