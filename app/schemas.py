"""
Pydantic models for proxy requests, responses, and tenant config.
OpenAI-compatible chat completion request/response for proxy passthrough.
"""
from typing import Any, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str  # system, user, assistant
    content: Optional[str] = None
    name: Optional[str] = None


class ChatRequest(BaseModel):
    """OpenAI-compatible chat completion request (subset we proxy)."""
    model: str = "gpt-4"
    messages: list[ChatMessage]
    stream: bool = False
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    tools: Optional[list[dict[str, Any]]] = None
    tool_choice: Optional[str | dict[str, Any]] = None


class ChatChoice(BaseModel):
    index: int = 0
    message: Optional[dict[str, Any]] = None
    delta: Optional[dict[str, Any]] = None
    finish_reason: Optional[str] = None


class ChatResponse(BaseModel):
    """OpenAI-compatible chat completion response."""
    id: Optional[str] = None
    object: str = "chat.completion"
    created: Optional[int] = None
    model: str = ""
    choices: list[ChatChoice] = []
    usage: Optional[dict[str, int]] = None


class TenantConfig(BaseModel):
    tenant_id: str
    rate_limit_rpm: int = 60
    allowed_models: list[str] = Field(default_factory=lambda: ["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet"])
    allow_tool_calls: bool = True
    system_prompt_override: Optional[str] = None


class AuditLogEntry(BaseModel):
    tenant_id: str
    user_id: Optional[str] = None
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: Optional[int] = None
    cost_usd: Optional[float] = None
    cache_hit: bool = False
    error_message: Optional[str] = None
