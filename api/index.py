import os
import httpx
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Lightweight version for Vercel serverless
app = FastAPI(title="GitHub Badge API - Vercel")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple badge generation for serverless
def generate_badge(label: str, value: str, style: str = "flat", color: str = "#4c1") -> str:
    width = max(80, len(label) * 8 + len(value) * 8 + 20)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="20">
<rect width="100%" height="100%" fill="{color}"/>
<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#fff" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">{label}: {value}</text>
</svg>'''

async def get_github_stars(owner: str, repo: str) -> str:
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.github.com/repos/{owner}/{repo}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            return str(data.get("stargazers_count", 0))
        return "0"

@app.get("/")
async def root():
    return HTMLResponse("""
    <h1>GitHub Badge API - Vercel Serverless</h1>
    <p>Example: <a href="/badge/github/microsoft/vscode/stars">Stars Badge</a></p>
    """)

@app.get("/badge/github/{owner}/{repo}/{metric}")
async def github_badge(owner: str, repo: str, metric: str, style: str = "flat", color: str = "#4c1"):
    if metric == "stars":
        value = await get_github_stars(owner, repo)
    else:
        value = "?"

    svg = generate_badge(metric, value, style, color)
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/badge/custom")
async def custom_badge(label: str = "Badge", value: str = "Value", style: str = "flat", color: str = "#4c1"):
    svg = generate_badge(label, value, style, color)
    return Response(content=svg, media_type="image/svg+xml")