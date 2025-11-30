from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import time
import asyncio
from typing import Optional
import hashlib

from .config import settings
from .badge import generate_badge
from .github import get_github_metric
from .cache import cache_get, cache_set
from .rate_limit import limiter
from .analytics import track_badge_render
from .plugins import load_plugins, get_plugin_metric

app = FastAPI(
    title="GitHub Badge API 2.0",
    description="A next-generation, ultra-fast, modular badge generation platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Mount static files for dashboard
app.mount("/static", StaticFiles(directory="dashboard/static"), name="static")
templates = Jinja2Templates(directory="dashboard/templates")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Badge-Generated-In"] = f"{process_time:.3f}s"
    # ETag for caching
    content = response.body
    etag = hashlib.md5(content).hexdigest()
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "public, max-age=300"
    return response

@app.on_event("startup")
async def startup_event():
    load_plugins()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "version": "2.0.0"})

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "2.0.0"}

# V1 endpoints (backward compatibility)
@app.get("/badge/github/{owner}/{repo}/{metric}")
@limiter.limit(settings.RATE_LIMIT)
async def github_badge_v1(request: Request, owner: str, repo: str, metric: str, style: str = "flat", color: Optional[str] = None, icon: str = ""):
    await track_badge_render("github", f"{owner}/{repo}", metric)
    cache_key = f"github:{owner}:{repo}:{metric}:{style}:{color}:{icon}"
    cached = await cache_get(cache_key)
    if cached:
        return Response(content=cached, media_type="image/svg+xml")

    try:
        value = await get_github_metric(owner, repo, metric)
        svg = generate_badge(metric, value, style=style, color=color, icon=icon)
        await cache_set(cache_key, svg, ttl=settings.CACHE_TTL)
        return Response(content=svg, media_type="image/svg+xml")
    except Exception as e:
        error_svg = generate_badge("error", "unknown", style=style, color="red")
        return Response(content=error_svg, media_type="image/svg+xml")

@app.get("/badge/custom")
@limiter.limit(settings.RATE_LIMIT)
async def custom_badge_v1(request: Request, label: str, value: str, style: str = "flat", color: Optional[str] = None, icon: str = ""):
    await track_badge_render("custom", label, value)
    cache_key = f"custom:{label}:{value}:{color}:{style}:{icon}"
    cached = await cache_get(cache_key)
    if cached:
        return Response(content=cached, media_type="image/svg+xml")

    svg = generate_badge(label, value, style=style, color=color, icon=icon)
    await cache_set(cache_key, svg, ttl=settings.CACHE_TTL)
    return Response(content=svg, media_type="image/svg+xml")

# V2 endpoints
@app.get("/v2/badge/github/{owner}/{repo}/{metric}")
@limiter.limit(settings.RATE_LIMIT)
async def github_badge_v2(request: Request, owner: str, repo: str, metric: str, style: str = "flat", color: Optional[str] = None, icon: str = "", format: str = "svg"):
    await track_badge_render("github", f"{owner}/{repo}", metric)
    cache_key = f"v2:github:{owner}:{repo}:{metric}:{style}:{color}:{icon}"
    cached = await cache_get(cache_key)
    if cached and format == "svg":
        return Response(content=cached, media_type="image/svg+xml")

    try:
        value = await get_github_metric(owner, repo, metric)
        if format == "json":
            return JSONResponse({"label": metric, "value": value, "style": style, "color": color, "icon": icon})
        svg = generate_badge(metric, value, style=style, color=color, icon=icon)
        await cache_set(cache_key, svg, ttl=settings.CACHE_TTL)
        return Response(content=svg, media_type="image/svg+xml")
    except Exception as e:
        if format == "json":
            return JSONResponse({"error": "unknown"}, status_code=404)
        error_svg = generate_badge("error", "unknown", style=style, color="red")
        return Response(content=error_svg, media_type="image/svg+xml")

@app.get("/v2/badge/custom")
@limiter.limit(settings.RATE_LIMIT)
async def custom_badge_v2(request: Request, label: str, value: str, style: str = "flat", color: Optional[str] = None, icon: str = "", format: str = "svg"):
    await track_badge_render("custom", label, value)
    cache_key = f"v2:custom:{label}:{value}:{color}:{style}:{icon}"
    cached = await cache_get(cache_key)
    if cached and format == "svg":
        return Response(content=cached, media_type="image/svg+xml")

    if format == "json":
        return JSONResponse({"label": label, "value": value, "style": style, "color": color, "icon": icon})
    svg = generate_badge(label, value, style=style, color=color, icon=icon)
    await cache_set(cache_key, svg, ttl=settings.CACHE_TTL)
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/v2/badge/plugin/{plugin}/{metric}")
@limiter.limit(settings.RATE_LIMIT)
async def plugin_badge(request: Request, plugin: str, metric: str, style: str = "flat", color: Optional[str] = None, icon: str = "", format: str = "svg"):
    await track_badge_render("plugin", plugin, metric)
    try:
        value = await get_plugin_metric(plugin, metric)
        if format == "json":
            return JSONResponse({"plugin": plugin, "metric": metric, "value": value})
        svg = generate_badge(metric, value, style=style, color=color, icon=icon)
        return Response(content=svg, media_type="image/svg+xml")
    except Exception as e:
        if format == "json":
            return JSONResponse({"error": "plugin not found"}, status_code=404)
        error_svg = generate_badge("error", "unknown", style=style, color="red")
        return Response(content=error_svg, media_type="image/svg+xml")

# Dashboard
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/analytics")
async def get_analytics():
    from .analytics import get_analytics as get_analytics_data
    return await get_analytics_data()

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