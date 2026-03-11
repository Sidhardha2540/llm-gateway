"""
Per-tenant rate limiting using Redis (sliding window / fixed window).
Limit: requests per minute per tenant.
"""
import time
from typing import Optional
from app.cache.redis_client import get_redis


RATE_LIMIT_PREFIX = "llm_gateway:rate:"
WINDOW_SECONDS = 60


async def check_rate_limit(tenant_id: str, limit_rpm: int) -> tuple[bool, int]:
    """
    Returns (allowed, current_count).
    Uses a simple fixed window: key = tenant_id, value = count, expire = 60s.
    """
    if limit_rpm <= 0:
        return True, 0

    r = await get_redis()
    key = f"{RATE_LIMIT_PREFIX}{tenant_id}"
    count = await r.incr(key)
    if count == 1:
        await r.expire(key, WINDOW_SECONDS)

    allowed = count <= limit_rpm
    return allowed, count


async def get_remaining(tenant_id: str, limit_rpm: int) -> int:
    r = await get_redis()
    key = f"{RATE_LIMIT_PREFIX}{tenant_id}"
    count = int(await r.get(key) or 0)
    return max(0, limit_rpm - count)
