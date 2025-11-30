from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import time
import asyncio
from typing import Optional

from .config import settings
from .badge import generate_badge
from .github import get_github_metric
from .cache import cache_get, cache_set
from .rate_limit import limiter

app = FastAPI(
    title="GitHub Badge API",
    description="A high-performance API for generating dynamic SVG badges for GitHub repositories",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Badge-Generated-In"] = f"{process_time:.3f}s"
    return response

@app.get("/")
async def root():
    return {"message": "GitHub Badge API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/badge/github/{owner}/{repo}/{metric}")
@limiter.limit(settings.RATE_LIMIT)
async def github_badge(request: Request, owner: str, repo: str, metric: str, style: str = "flat", color: Optional[str] = None):
    cache_key = f"github:{owner}:{repo}:{metric}:{style}:{color}"
    cached = await cache_get(cache_key)
    if cached:
        return Response(content=cached, media_type="image/svg+xml")

    try:
        value = await get_github_metric(owner, repo, metric)
        svg = generate_badge(metric, value, style=style, color=color)
        await cache_set(cache_key, svg, ttl=settings.CACHE_TTL)
        return Response(content=svg, media_type="image/svg+xml")
    except Exception as e:
        error_svg = generate_badge("error", "unknown", style=style, color="red")
        return Response(content=error_svg, media_type="image/svg+xml")

@app.get("/badge/custom")
@limiter.limit(settings.RATE_LIMIT)
async def custom_badge(request: Request, label: str, value: str, color: str = "blue", style: str = "flat"):
    cache_key = f"custom:{label}:{value}:{color}:{style}"
    cached = await cache_get(cache_key)
    if cached:
        return Response(content=cached, media_type="image/svg+xml")

    svg = generate_badge(label, value, style=style, color=color)
    await cache_set(cache_key, svg, ttl=settings.CACHE_TTL)
    return Response(content=svg, media_type="image/svg+xml")