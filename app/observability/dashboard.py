"""
Dashboard API endpoints: usage, latency, cache hit rate, errors.
Data from PostgreSQL (audit_log, usage_aggregates).
"""
from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Query

from app.db import init_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/usage")
async def get_usage(
    tenant_id: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=90),
):
    """Per-tenant token consumption over the last N days."""
    pool = await init_db()
    end = date.today()
    start = end - timedelta(days=days)
    async with pool.acquire() as conn:
        if tenant_id:
            rows = await conn.fetch(
                """
                SELECT tenant_id, date, provider, total_requests, total_prompt_tokens,
                       total_completion_tokens, total_cost_usd, cache_hits, errors
                FROM usage_aggregates
                WHERE tenant_id = $1 AND date >= $2 AND date <= $3
                ORDER BY date DESC, provider
                """,
                tenant_id,
                start,
                end,
            )
        else:
            rows = await conn.fetch(
                """
                SELECT tenant_id, date, provider, total_requests, total_prompt_tokens,
                       total_completion_tokens, total_cost_usd, cache_hits, errors
                FROM usage_aggregates
                WHERE date >= $1 AND date <= $2
                ORDER BY date DESC, tenant_id, provider
                """,
                start,
                end,
            )
    return [dict(r) for r in rows]


@router.get("/latency")
async def get_latency(
    tenant_id: Optional[str] = Query(None),
    provider: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
):
    """Latency per provider (from audit_log)."""
    pool = await init_db()
    async with pool.acquire() as conn:
        if tenant_id and provider:
            rows = await conn.fetch(
                """
                SELECT provider, model, AVG(latency_ms) as avg_latency_ms,
                       COUNT(*) as request_count
                FROM audit_log
                WHERE tenant_id = $1 AND provider = $2 AND latency_ms IS NOT NULL
                GROUP BY provider, model
                LIMIT $3
                """,
                tenant_id,
                provider,
                limit,
            )
        elif tenant_id:
            rows = await conn.fetch(
                """
                SELECT provider, model, AVG(latency_ms) as avg_latency_ms,
                       COUNT(*) as request_count
                FROM audit_log
                WHERE tenant_id = $1 AND latency_ms IS NOT NULL
                GROUP BY provider, model
                LIMIT $3
                """,
                tenant_id,
                limit,
            )
        else:
            rows = await conn.fetch(
                """
                SELECT provider, model, AVG(latency_ms) as avg_latency_ms,
                       COUNT(*) as request_count
                FROM audit_log
                WHERE latency_ms IS NOT NULL
                GROUP BY provider, model
                LIMIT $1
                """,
                limit,
            )
    return [dict(r) for r in rows]


@router.get("/cache")
async def get_cache_stats(
    tenant_id: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=90),
):
    """Cache hit rate over time."""
    pool = await init_db()
    end = date.today()
    start = end - timedelta(days=days)
    async with pool.acquire() as conn:
        if tenant_id:
            row = await conn.fetchrow(
                """
                SELECT
                    COUNT(*) FILTER (WHERE cache_hit) as hits,
                    COUNT(*) as total
                FROM audit_log
                WHERE tenant_id = $1 AND created_at >= $2
                """,
                tenant_id,
                start,
            )
        else:
            row = await conn.fetchrow(
                """
                SELECT
                    COUNT(*) FILTER (WHERE cache_hit) as hits,
                    COUNT(*) as total
                FROM audit_log
                WHERE created_at >= $1
                """,
                start,
            )
    total = row["total"] or 0
    hits = row["hits"] or 0
    hit_rate = (hits / total * 100) if total else 0
    return {"cache_hits": hits, "total_requests": total, "hit_rate_pct": round(hit_rate, 2)}


@router.get("/errors")
async def get_errors(
    tenant_id: Optional[str] = Query(None),
    provider: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
):
    """Error rates by provider (from audit_log where error_message IS NOT NULL)."""
    pool = await init_db()
    async with pool.acquire() as conn:
        if tenant_id:
            rows = await conn.fetch(
                """
                SELECT provider, model, COUNT(*) as error_count
                FROM audit_log
                WHERE tenant_id = $1 AND error_message IS NOT NULL
                GROUP BY provider, model
                LIMIT $2
                """,
                tenant_id,
                limit,
            )
        else:
            rows = await conn.fetch(
                """
                SELECT provider, model, COUNT(*) as error_count
                FROM audit_log
                WHERE error_message IS NOT NULL
                GROUP BY provider, model
                LIMIT $1
                """,
                limit,
            )
    return [dict(r) for r in rows]
