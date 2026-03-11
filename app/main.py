"""
FastAPI app: proxy endpoint + dashboard routes.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.proxy import proxy_chat
from app.observability.dashboard import router as dashboard_router
from app.db import init_db, close_db
from app.cache.redis_client import close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()
    await close_redis()


app = FastAPI(
    title="LLM Gateway",
    description="API proxy with semantic caching, rate limiting, and observability",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(dashboard_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """OpenAI-compatible chat completion endpoint. Use X-Tenant-ID header for tenant."""
    body = await request.json()
    return await proxy_chat(request, body)


@app.get("/")
async def root():
    return {
        "service": "LLM Gateway",
        "docs": "/docs",
        "health": "/health",
        "chat": "POST /v1/chat/completions",
        "dashboard": "/dashboard/usage | /dashboard/latency | /dashboard/cache | /dashboard/errors",
    }
