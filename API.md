# API Reference

## Endpoints

### GitHub Badges

`GET /v2/badge/github/{owner}/{repo}/{metric}`

Parameters:
- `style`: flat, minimal, neon, cyberpunk, glass, pixel
- `color`: hex color or named
- `icon`: github, star, flame, bolt
- `animated`: true/false
- `format`: svg (default), json

### Custom Badges

`GET /v2/badge/custom`

Parameters: label, value, style, color, icon, animated, format

### Plugin Badges

`GET /v2/badge/plugin/{plugin}/{metric}`

### Badge Composition

`GET /v2/compose`

Parameters:
- `badges`: comma-separated list (e.g., "stars:100,forks:50")
- `layout`: horizontal, vertical

### WebSocket Live Stats

`WS /ws/live/{provider}/{owner}/{repo}`

Streams live badge data as JSON.

### Dashboard

`GET /dashboard` - Main dashboard UI

`GET /dashboard/analytics` - Analytics data

## Rate Limits

- 100 requests/minute per IP
- Configurable via environment

## Caching

- ETags for browser caching
- 5-minute TTL by default