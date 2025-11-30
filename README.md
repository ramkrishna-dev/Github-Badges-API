# GitHub Badge API 3.5

The FINAL and MOST ADVANCED Python-powered badge generation platform. Ultra-modular, hyper-fast, with dynamic SVG rendering, multi-provider stats, animations, plugins, caching, insight analytics, themes, dashboards, automation, and CDN-ready deployment. 100% Python, ZERO AI.

## Features

- **Modular Badge Engine**: `/src/badges/` with dynamic SVG templates
- **Animated SVG Badges**: SMIL/CSS animations, gradients, glow, pulse effects
- **Realtime Streaming**: WebSocket `/ws/live/<metric>` for live stats
- **Multi-Provider Stats**: GitHub, GitLab, Bitbucket, Docker Hub, PyPI, NPM, YouTube, Twitter/X
- **Deep Insight Badges**: Commit velocity, issue resolution, activity rank, heatmap
- **Trophy System**: Bronze/Silver/Gold/Diamond/Legendary auto-awards
- **Badge Composition**: `/v2/compose` for multi-badge layouts
- **Advanced Themes**: 9 themes (classic, flat, pixel, neon, cyberpunk, glass, hacker-green, minimal, transparent)
- **Plugin Ecosystem**: Hot-reload Python modules in `/plugins/`
- **Developer Dashboard**: `/dashboard` with previewer, analytics, theme editor
- **Analytics System**: SQLite/Redis tracking renders, cache hits, popular badges
- **Caching & CDN**: ETag, Last-Modified, pre-cached popular badges
- **Security**: HMAC-signed URLs, API keys, rate limiting, abuse detection
- **Automation**: APScheduler cron jobs, GitHub `/webhook/github` for cache refresh

## Quick Start

### Using Docker Compose

```bash
git clone https://github.com/Code-Xon/github-badge-api.git
cd github-badge-api
docker-compose up
```

### Manual Installation

```bash
pip install -e .
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### V2 GitHub Badges

`GET /v2/badge/github/{owner}/{repo}/{metric}?style=flat&color=blue&icon=github&animated=false&format=svg`

Supported metrics: stars, forks, watchers, open_issues, open_prs, last_commit, contributors, size, release, license, ci_status, commit_frequency, activity_rank

Example: `https://your-api.com/v2/badge/github/microsoft/vscode/stars?style=neon&animated=true&format=json`

### V2 Custom Badges

`GET /v2/badge/custom?label=Hello&value=World&color=blue&style=flat&icon=star&animated=false&format=svg`

Example: `https://your-api.com/v2/badge/custom?label=Build&value=Passing&color=green&style=cyberpunk&animated=true`

### V2 Plugin Badges

`GET /v2/badge/plugin/{plugin}/{metric}?style=flat&animated=false&format=svg`

Example: `https://your-api.com/v2/badge/plugin/system/cpu`

### Badge Composition

`GET /v2/compose?badges=stars:100,forks:50&layout=horizontal`

### Theme Management

`GET /themes/list` - List available themes
`POST /themes/install?url=<url>` - Install theme from URL

### Plugin Management

`GET /plugins/list` - List loaded plugins

### Webhooks

`POST /webhook/github` - GitHub webhook for cache refresh

### Realtime Streaming

`WS /ws/live/{provider}/{owner}/{repo}` - Live badge stats via WebSocket

### V1 Compatibility

V1 endpoints are maintained for backward compatibility.

## Configuration

Create a `.env` file:

```env
GITHUB_TOKEN=your_github_token  # Optional, increases rate limits
REDIS_URL=redis://localhost:6379  # Optional, for Redis caching
RATE_LIMIT=100/minute
CACHE_TTL=300
```

## Deployment

### Docker Compose

```bash
docker-compose up -d
```

### Kubernetes

```bash
kubectl apply -f k8s/
```

### Railway

1. Connect repo
2. Set env vars: GITHUB_TOKEN, REDIS_URL
3. Deploy

### Render

1. Web Service
2. Build: `pip install -e .`
3. Start: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

### Vercel (Serverless)

Use Vercel Python runtime.

### Fly.io

```bash
fly launch
fly deploy
```

### Cloudflare Workers

A JavaScript version is available for edge deployment:

1. Install Wrangler: `npm install -g wrangler`
2. Set your GitHub token: `wrangler secret put GITHUB_TOKEN`
3. Deploy: `wrangler deploy`

Example URLs:
- `https://your-worker.workers.dev/badge/github/microsoft/vscode/stars`
- `https://your-worker.workers.dev/badge/custom?label=Build&value=Passing`

### Cloudflare Workers

Edge deployment guide in docs.

## Caching

- In-memory caching by default (300s TTL)
- Optional Redis for distributed caching
- Automatic cache invalidation

## Rate Limiting

- Default: 100 requests per minute per IP
- Configurable via `RATE_LIMIT` env var

## Code Structure

```
src/
├── main.py          # FastAPI app, routes, dashboard
├── badge.py         # Modular badge engine
├── github.py        # GitHub API client
├── cache.py         # CDN caching
├── config.py        # Settings
├── rate_limit.py    # Rate limiting
├── analytics.py     # Analytics tracking
├── plugins.py       # Plugin loader
└── utils.py         # Utilities
plugins/             # Plugin modules
dashboard/           # Web UI templates/static
tests/               # Tests
k8s/                 # Kubernetes manifests
```

## Development

```bash
pip install -e ".[dev]"
pytest
black src/
ruff src/
```

## Plugins

Extend the API with custom badge providers. Example plugins:

- **system**: CPU, memory, disk usage
- **discord**: Server member count
- **twitter**: Follower count

Create `plugins/your_plugin.py` with `async def get_metric(metric: str) -> str`.

## Analytics

View badge usage at `/dashboard` or `/api/analytics`.

## API Documentation

- Interactive docs: `/docs`
- ReDoc: `/redoc`
- Dashboard: `/dashboard`

## Acknowledgments

- **Organization**: Code-Xon
- **Lead Developer**: Ramkrishna
- **Co-Developer**: Razzak

Inspired by Shields.io. Built for the open-source community.