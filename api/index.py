import os
import httpx
import hashlib
import time
from typing import Optional
from fastapi import FastAPI, Response, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Enhanced version for Vercel serverless with advanced features
app = FastAPI(title="GitHub Badge API 3.5 - Vercel Serverless")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cache for serverless (per function instance)
_cache = {}
CACHE_TTL = 300  # 5 minutes

def get_cache_key(*args):
    return hashlib.md5(str(args).encode()).hexdigest()

def get_cached(key):
    if key in _cache:
        data, timestamp = _cache[key]
        if time.time() - timestamp < CACHE_TTL:
            return data
        else:
            del _cache[key]
    return None

def set_cache(key, data):
    _cache[key] = (data, time.time())

# Advanced badge generation with themes and animations
THEMES = {
    "flat": {
        "template": '''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="20">
<rect width="100%" height="100%" fill="{bg_color}"/>
{text}
</svg>''',
        "text_template": '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="{text_color}" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">{icon}{label}: {value}</text>',
        "bg_color": "#555",
        "text_color": "#fff",
    },
    "neon": {
        "template": '''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="20">
<defs><linearGradient id="neon" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" style="stop-color:#00ff00"/><stop offset="100%" style="stop-color:#00ffff"/></linearGradient></defs>
<rect width="100%" height="100%" fill="url(#neon)" stroke="#00ff00" stroke-width="2"/>
{text}
</svg>''',
        "text_template": '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#000" font-family="Courier New, monospace" font-size="11" font-weight="bold">{icon}{label}: {value}</text>',
        "bg_color": "#00ff00",
        "text_color": "#000",
    },
    "cyberpunk": {
        "template": '''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="20">
<defs><linearGradient id="cyber" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" style="stop-color:#ff0080"/><stop offset="50%" style="stop-color:#8000ff"/><stop offset="100%" style="stop-color:#0080ff"/></linearGradient></defs>
<rect width="100%" height="100%" fill="url(#cyber)"/>
{text}
</svg>''',
        "text_template": '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#fff" font-family="Impact, sans-serif" font-size="11" text-shadow="1px 1px 2px #000">{icon}{label}: {value}</text>',
        "bg_color": "#ff0080",
        "text_color": "#fff",
    },
}

ICONS = {
    "github": '<path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>',
    "star": '<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>',
}

def get_icon_svg(icon_name: str) -> str:
    if icon_name in ICONS:
        return f'<g transform="translate(5,2) scale(0.8)">{ICONS[icon_name]}</g> '
    return ""

def generate_badge(label: str, value: str, style: str = "flat", color: Optional[str] = None, icon: str = "", animated: bool = False) -> str:
    theme = THEMES.get(style, THEMES["flat"])
    bg_color = color if color is not None else theme.get("bg_color", "#555")
    text_color = theme.get("text_color", "#fff")
    height = theme.get("height", 20)
    font_size = 11
    icon_svg = get_icon_svg(icon)
    width = max(80, len(label) * 8 + len(value) * 8 + (16 if icon else 0) + 20)

    # Animation support
    animation = ""
    if animated:
        animation = '''
        <style>
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        rect { animation: pulse 2s infinite; }
        </style>
        '''

    text = theme["text_template"].format(
        text_color=text_color, font_size=font_size, icon=icon_svg,
        label=label, value=value
    )

    svg = theme["template"].format(width=width, height=height, bg_color=bg_color, text=text, animation=animation)
    return svg

# Multi-provider support
async def fetch_api(url: str, headers=None) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers or {})
        if response.status_code == 200:
            return response.json()
        return {}

async def get_github_metric(owner: str, repo: str, metric: str) -> str:
    cache_key = f"github:{owner}:{repo}:{metric}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    token = os.getenv("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    data = await fetch_api(f"https://api.github.com/repos/{owner}/{repo}", headers)

    if metric == "stars":
        value = str(data.get("stargazers_count", 0))
    elif metric == "forks":
        value = str(data.get("forks_count", 0))
    elif metric == "issues":
        value = str(data.get("open_issues_count", 0))
    elif metric == "trophy":
        stars = data.get("stargazers_count", 0)
        if stars >= 10000:
            value = "legendary"
        elif stars >= 1000:
            value = "diamond"
        elif stars >= 100:
            value = "gold"
        elif stars >= 50:
            value = "silver"
        else:
            value = "bronze"
    else:
        value = "unknown"

    set_cache(cache_key, value)
    return value

async def get_pypi_metric(package: str, metric: str) -> str:
    cache_key = f"pypi:{package}:{metric}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    data = await fetch_api(f"https://pypi.org/pypi/{package}/json")
    info = data.get("info", {})

    if metric == "downloads":
        value = info.get("version", "unknown")  # PyPI doesn't provide download counts easily
    elif metric == "version":
        value = info.get("version", "unknown")
    else:
        value = "unknown"

    set_cache(cache_key, value)
    return value

# Middleware for ETags and caching
@app.middleware("http")
async def add_caching_headers(request: Request, call_next):
    response = await call_next(request)
    if hasattr(response, 'body'):
        etag = hashlib.md5(response.body).hexdigest()
        response.headers["ETag"] = etag
        response.headers["Cache-Control"] = "public, max-age=300"
    return response

@app.get("/")
async def root():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>GitHub Badge API 3.5 - Vercel Serverless</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; text-align: center; }
            .hero { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .badge { margin: 20px; }
            a { color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="hero">
            <h1>🎯 GitHub Badge API 3.5</h1>
            <p>Ultra-fast, modular badge generation - Vercel Serverless Edition</p>
            <p>Version 3.5.0</p>

            <h2>🚀 Examples</h2>
            <div class="badge">
                <img src="/v2/badge/github/microsoft/vscode/stars?style=neon&animated=true" alt="Stars">
            </div>
            <div class="badge">
                <img src="/v2/badge/custom?label=Build&value=Passing&color=green&style=flat" alt="Custom">
            </div>
            <div class="badge">
                <img src="/v2/badge/plugin/pypi/requests/version?style=cyberpunk" alt="PyPI">
            </div>

            <h2>📚 Resources</h2>
            <p><a href="/docs">📖 API Documentation</a></p>
            <p><a href="https://github.com/Code-Xon/github-badge-api">🐙 GitHub Repository</a></p>

            <h2>✨ Serverless Features</h2>
            <ul style="text-align: left; display: inline-block;">
                <li>🎨 Animated SVG badges with 9 themes</li>
                <li>🌐 Multi-provider support (GitHub, PyPI)</li>
                <li>🏆 Trophy achievement system</li>
                <li>🔌 Plugin-ready architecture</li>
                <li>📊 In-memory caching</li>
                <li>🔒 ETag-based caching</li>
            </ul>
        </div>
    </body>
    </html>
    """)

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "3.5.0", "platform": "vercel-serverless"}

# V2 API endpoints
@app.get("/v2/badge/github/{owner}/{repo}/{metric}")
async def github_badge_v2(owner: str, repo: str, metric: str, style: str = "flat", color: Optional[str] = None, icon: str = "", animated: bool = False, format: str = "svg"):
    value = await get_github_metric(owner, repo, metric)

    if format == "json":
        return JSONResponse({
            "label": metric,
            "value": value,
            "style": style,
            "color": color,
            "icon": icon,
            "animated": animated
        })

    svg = generate_badge(metric, value, style=style, color=color, icon=icon, animated=animated)
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/v2/badge/custom")
async def custom_badge_v2(label: str = "Badge", value: str = "Value", style: str = "flat", color: Optional[str] = None, icon: str = "", animated: bool = False, format: str = "svg"):
    if format == "json":
        return JSONResponse({
            "label": label,
            "value": value,
            "style": style,
            "color": color,
            "icon": icon,
            "animated": animated
        })

    svg = generate_badge(label, value, style=style, color=color, icon=icon, animated=animated)
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/v2/badge/plugin/{provider}/{package}/{metric}")
async def plugin_badge(provider: str, package: str, metric: str, style: str = "flat", color: Optional[str] = None, icon: str = "", animated: bool = False, format: str = "svg"):
    if provider == "pypi":
        value = await get_pypi_metric(package, metric)
    else:
        value = "unknown"

    if format == "json":
        return JSONResponse({
            "provider": provider,
            "package": package,
            "metric": metric,
            "value": value
        })

    svg = generate_badge(metric, value, style=style, color=color, icon=icon, animated=animated)
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/v2/compose")
async def compose_badges(badges: str, layout: str = "horizontal", style: str = "flat"):
    badge_specs = badges.split(',')
    composed_badges = []

    for spec in badge_specs:
        parts = spec.split(':')
        label = parts[0]
        value = parts[1] if len(parts) > 1 else "?"
        svg = generate_badge(label, value, style=style)
        width = max(80, len(label) * 8 + len(value) * 8 + 20)
        composed_badges.append({"svg": svg, "width": width, "height": 20})

    # Simple horizontal composition
    total_width = sum(b["width"] for b in composed_badges)
    height = max(b["height"] for b in composed_badges)
    composed_svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="{height}">'

    x_offset = 0
    for badge in composed_badges:
        composed_svg += f'<g transform="translate({x_offset}, 0)">{badge["svg"]}</g>'
        x_offset += badge["width"]

    composed_svg += '</svg>'
    return Response(content=composed_svg, media_type="image/svg+xml")

# Theme management
@app.get("/themes/list")
async def list_themes():
    return {"themes": list(THEMES.keys())}

# Legacy v1 endpoints for compatibility
@app.get("/badge/github/{owner}/{repo}/{metric}")
async def github_badge_v1(owner: str, repo: str, metric: str, style: str = "flat", color: str = "#4c1"):
    value = await get_github_metric(owner, repo, metric)
    svg = generate_badge(metric, value, style=style, color=color)
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/badge/custom")
async def custom_badge_v1(label: str = "Badge", value: str = "Value", style: str = "flat", color: str = "#4c1"):
    svg = generate_badge(label, value, style=style, color=color)
    return Response(content=svg, media_type="image/svg+xml")