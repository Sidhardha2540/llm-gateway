"""
Structured audit logging: write every LLM request to PostgreSQL.
"""
from datetime import date
from typing import Optional

from app import db


async def log_request(
    tenant_id: str,
    user_id: Optional[str],
    provider: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    latency_ms: Optional[int] = None,
    cost_usd: Optional[float] = None,
    cache_hit: bool = False,
    error_message: Optional[str] = None,
) -> None:
    await db.insert_audit_log(
        tenant_id=tenant_id,
        user_id=user_id,
        provider=provider,
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        latency_ms=latency_ms,
        cost_usd=cost_usd,
        cache_hit=cache_hit,
        error_message=error_message,
    )
    date_str = date.today().isoformat()
    await db.upsert_usage(
        tenant_id=tenant_id,
        date_str=date_str,
        provider=provider,
        requests_delta=1,
        prompt_tokens_delta=prompt_tokens,
        completion_tokens_delta=completion_tokens,
        cost_delta=cost_usd or 0,
        cache_hits_delta=1 if cache_hit else 0,
        errors_delta=1 if error_message else 0,
    )
