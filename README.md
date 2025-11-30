# GitHub Badge API

A high-performance, scalable API for generating dynamic SVG badges for GitHub repositories, similar to Shields.io. Built with FastAPI for optimal performance and async operations.

## Features

- **GitHub Metrics Badges**: Stars, forks, watchers, open issues/PRs, last commit, contributors, repo size, release version, license, CI status
- **Custom Badges**: Create custom badges with any label and value
- **Badge Styling**: Multiple themes (flat, flat-square, plastic, minimal) with dynamic color detection
- **Performance**: In-memory + optional Redis caching, async GitHub API fetching
- **Rate Limiting**: Configurable request rate limiting
- **Self-Hostable**: Easy deployment with Docker

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

### GitHub Badges

`GET /badge/github/{owner}/{repo}/{metric}?style=flat&color=blue`

Supported metrics:
- `stars` - Repository stars
- `forks` - Repository forks
- `watchers` - Repository watchers
- `open_issues` - Open issues count
- `open_prs` - Open pull requests count
- `last_commit` - Last commit date
- `contributors` - Contributors count
- `size` - Repository size (KB)
- `release` - Latest release tag
- `license` - Repository license
- `ci_status` - GitHub Actions status

Example: `https://your-api.com/badge/github/microsoft/vscode/stars`

### Custom Badges

`GET /badge/custom?label=Hello&value=World&color=blue&style=flat`

Example: `https://your-api.com/badge/custom?label=Build&value=Passing&color=green`

## Configuration

Create a `.env` file:

```env
GITHUB_TOKEN=your_github_token  # Optional, increases rate limits
REDIS_URL=redis://localhost:6379  # Optional, for Redis caching
RATE_LIMIT=100/minute
CACHE_TTL=300
```

## Deployment

### Railway

1. Connect your GitHub repo
2. Set environment variables
3. Deploy

### Render

1. Create a new Web Service
2. Connect repo, set build command: `pip install -e .`
3. Start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

### Vercel (Serverless)

Use Vercel Python runtime.

### Fly.io

```bash
fly launch
fly deploy
```

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
├── main.py          # FastAPI app and routes
├── badge.py         # SVG badge generation
├── github.py        # GitHub API client
├── cache.py         # Caching layer
├── config.py        # Configuration
├── rate_limit.py    # Rate limiting
└── utils.py         # Utilities
tests/               # Unit and integration tests
```

## Development

```bash
pip install -e ".[dev]"
pytest
black src/
ruff src/
```

## API Documentation

- Interactive docs: `/docs`
- ReDoc: `/redoc`

## Acknowledgments

- **Organization**: Code-Xon
- **Lead Developer**: Ramkrishna
- **Co-Developer**: Razzak

Inspired by Shields.io