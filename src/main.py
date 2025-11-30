from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import time
import asyncio
from typing import Optional, List
import hashlib
import json

from .config import settings
from .badges import generate_badge
from .providers.github import get_github_metric
from .cache import cache_get, cache_set
from .rate_limit import limiter
from .analytics import track_badge_render, init_db
from .plugins import load_plugins, get_plugin_metric
from .themes import get_theme
from .dashboard import router as dashboard_router

app = FastAPI(
    title="GitHub Badge API 3.0",
    description="A hyper-modular, ultra-fast, future-proof badge generation platform",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Mount static files for dashboard
app.mount("/static", StaticFiles(directory="src/dashboard/static"), name="static")
templates = Jinja2Templates(directory="src/dashboard/templates")

# Include dashboard router
app.include_router(dashboard_router)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Badge-Generated-In"] = f"{process_time:.3f}s"
    # ETag for caching (only for Response, not StreamingResponse)
    if hasattr(response, 'body'):
        content = response.body
        etag = hashlib.md5(content).hexdigest()
        response.headers["ETag"] = etag
        response.headers["Cache-Control"] = "public, max-age=300"
    return response

@app.on_event("startup")
async def startup_event():
    await init_db()
    load_plugins()
    # Start background tasks
    from .scheduler import start_scheduler
    start_scheduler()

# WebSocket for live badges
@app.websocket("/ws/live/{provider}/{owner}/{repo}")
async def websocket_live_badge(websocket: WebSocket, provider: str, owner: str, repo: str):
    await websocket.accept()
    try:
        while True:
            # Send live stats every 30 seconds
            if provider == "github":
                stars = await get_github_metric(owner, repo, "stars")
                forks = await get_github_metric(owner, repo, "forks")
                data = {"stars": stars, "forks": forks, "timestamp": time.time()}
                await websocket.send_json(data)
            await asyncio.sleep(30)
    except WebSocketDisconnect:
        pass

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "version": "3.0.0"})

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
async def github_badge_v2(request: Request, owner: str, repo: str, metric: str, style: str = "flat", color: Optional[str] = None, icon: str = "", animated: bool = False, format: str = "svg"):
    await track_badge_render("github", f"{owner}/{repo}", metric)
    cache_key = f"v2:github:{owner}:{repo}:{metric}:{style}:{color}:{icon}:{animated}"
    cached = await cache_get(cache_key)
    if cached and format == "svg":
        return Response(content=cached, media_type="image/svg+xml")

    try:
        value = await get_github_metric(owner, repo, metric)
        if format == "json":
            return JSONResponse({"label": metric, "value": value, "style": style, "color": color, "icon": icon, "animated": animated})
        svg = generate_badge(metric, value, style=style, color=color, icon=icon, animated=animated)
        await cache_set(cache_key, svg, ttl=settings.CACHE_TTL)
        return Response(content=svg, media_type="image/svg+xml")
    except Exception as e:
        if format == "json":
            return JSONResponse({"error": "unknown"}, status_code=404)
        error_svg = generate_badge("error", "unknown", style=style, color="red")
        return Response(content=error_svg, media_type="image/svg+xml")

@app.get("/v2/badge/custom")
@limiter.limit(settings.RATE_LIMIT)
async def custom_badge_v2(request: Request, label: str, value: str, style: str = "flat", color: Optional[str] = None, icon: str = "", animated: bool = False, format: str = "svg"):
    await track_badge_render("custom", label, value)
    cache_key = f"v2:custom:{label}:{value}:{color}:{style}:{icon}:{animated}"
    cached = await cache_get(cache_key)
    if cached and format == "svg":
        return Response(content=cached, media_type="image/svg+xml")

    if format == "json":
        return JSONResponse({"label": label, "value": value, "style": style, "color": color, "icon": icon, "animated": animated})
    svg = generate_badge(label, value, style=style, color=color, icon=icon, animated=animated)
    await cache_set(cache_key, svg, ttl=settings.CACHE_TTL)
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/v2/badge/plugin/{plugin}/{metric}")
@limiter.limit(settings.RATE_LIMIT)
async def plugin_badge(request: Request, plugin: str, metric: str, style: str = "flat", color: Optional[str] = None, icon: str = "", animated: bool = False, format: str = "svg"):
    await track_badge_render("plugin", plugin, metric)
    try:
        value = await get_plugin_metric(plugin, metric)
        if format == "json":
            return JSONResponse({"plugin": plugin, "metric": metric, "value": value})
        svg = generate_badge(metric, value, style=style, color=color, icon=icon, animated=animated)
        return Response(content=svg, media_type="image/svg+xml")
    except Exception as e:
        if format == "json":
            return JSONResponse({"error": "plugin not found"}, status_code=404)
        error_svg = generate_badge("error", "unknown", style=style, color="red")
        return Response(content=error_svg, media_type="image/svg+xml")

@app.get("/v2/compose")
@limiter.limit(settings.RATE_LIMIT)
async def compose_badges_endpoint(request: Request, badges: str, layout: str = "horizontal", style: str = "flat"):
    badge_list = badges.split(',')
    composed_badges = []
    for badge_spec in badge_list:
        # Simple parsing: assume format like "stars:100" or just "stars"
        parts = badge_spec.split(':')
        label = parts[0]
        value = parts[1] if len(parts) > 1 else "?"
        svg = generate_badge(label, value, style=style)
        width = len(label) * 8 + len(value) * 8 + 40
        composed_badges.append({"svg": svg, "width": width, "height": 20})

    from .composer import compose_badges as compose_func
    final_svg = compose_func(composed_badges, layout)
    return Response(content=final_svg, media_type="image/svg+xml")

# Theme endpoints
@app.get("/themes/list")
async def list_themes():
    from .theme_engine import list_themes
    return list_themes()

@app.post("/themes/install")
async def install_theme(url: str):
    from .theme_engine import install_theme
    success = install_theme(url)
    return {"success": success}

# Plugin endpoints
@app.get("/plugins/list")
async def list_plugins():
    from .plugin_loader import list_plugins
    return {"plugins": list_plugins()}

# Webhook endpoint
@app.post("/webhook/github")
async def github_webhook(request: Request):
    # Handle GitHub webhook for cache refresh
    data = await request.json()
    # Refresh cache for the repo
    return {"status": "ok"}

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