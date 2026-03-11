"""
Model fallback: on timeout or provider error, try a fallback model (e.g. GPT-4 -> GPT-3.5).
"""
from typing import Optional

# Map primary model -> fallback model for OpenAI
OPENAI_FALLBACK = {
    "gpt-4": "gpt-3.5-turbo",
    "gpt-4-turbo": "gpt-3.5-turbo",
    "gpt-4o": "gpt-3.5-turbo",
}

# Anthropic fallbacks
ANTHROPIC_FALLBACK = {
    "claude-3-opus-20240229": "claude-3-sonnet-20240229",
    "claude-3-5-sonnet-20241022": "claude-3-haiku-20240307",
}


def get_fallback_model(provider: str, model: str) -> Optional[str]:
    if provider == "openai":
        return OPENAI_FALLBACK.get(model)
    if provider == "anthropic":
        return ANTHROPIC_FALLBACK.get(model)
    return None


def get_provider(model: str) -> str:
    if model.startswith("claude-"):
        return "anthropic"
    return "openai"
