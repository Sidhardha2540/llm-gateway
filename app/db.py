"""
PostgreSQL connection and helpers for audit log and usage.
Uses asyncpg for async connection pool.
"""
import os
import asyncpg
from datetime import date
from contextlib import asynccontextmanager
from typing import Optional

_pool: Optional[asyncpg.Pool] = None


def get_database_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/llm_gateway",
    )


async def init_db() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            get_database_url(),
            min_size=1,
            max_size=10,
            command_timeout=60,
        )
    return _pool


async def close_db() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


@asynccontextmanager
async def get_conn():
    pool = await init_db()
    async with pool.acquire() as conn:
        yield conn


async def insert_audit_log(
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
    pool = await init_db()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO audit_log (
                tenant_id, user_id, provider, model,
                prompt_tokens, completion_tokens, total_tokens,
                latency_ms, cost_usd, cache_hit, error_message
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            """,
            tenant_id,
            user_id,
            provider,
            model,
            prompt_tokens,
            completion_tokens,
            total_tokens,
            latency_ms,
            cost_usd,
            cache_hit,
            error_message,
        )


async def get_tenant_config(tenant_id: str) -> Optional[dict]:
    pool = await init_db()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT tenant_id, rate_limit_rpm, allowed_models, allow_tool_calls, system_prompt_override FROM tenant_config WHERE tenant_id = $1",
            tenant_id,
        )
        return dict(row) if row else None


async def upsert_usage(
    tenant_id: str,
    date_str: str,
    provider: str,
    requests_delta: int = 0,
    prompt_tokens_delta: int = 0,
    completion_tokens_delta: int = 0,
    cost_delta: float = 0,
    cache_hits_delta: int = 0,
    errors_delta: int = 0,
) -> None:
    usage_date = date.fromisoformat(date_str)
    pool = await init_db()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO usage_aggregates (
                tenant_id, date, provider,
                total_requests, total_prompt_tokens, total_completion_tokens,
                total_cost_usd, cache_hits, errors
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT (tenant_id, date, provider) DO UPDATE SET
                total_requests = usage_aggregates.total_requests + EXCLUDED.total_requests,
                total_prompt_tokens = usage_aggregates.total_prompt_tokens + EXCLUDED.total_prompt_tokens,
                total_completion_tokens = usage_aggregates.total_completion_tokens + EXCLUDED.total_completion_tokens,
                total_cost_usd = usage_aggregates.total_cost_usd + EXCLUDED.total_cost_usd,
                cache_hits = usage_aggregates.cache_hits + EXCLUDED.cache_hits,
                errors = usage_aggregates.errors + EXCLUDED.errors
            """,
            tenant_id,
            usage_date,
            provider,
            requests_delta,
            prompt_tokens_delta,
            completion_tokens_delta,
            cost_delta,
            cache_hits_delta,
            errors_delta,
        )
