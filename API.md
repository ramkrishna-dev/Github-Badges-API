# API Reference

## Endpoints

### GitHub Badges

`GET /v2/badge/github/{owner}/{repo}/{metric}`

Parameters:
- `style`: flat, flat-square, plastic, minimal, neon, cyberpunk, transparent
- `color`: named color or hex
- `icon`: github, star, flame, bolt
- `format`: svg (default), json

Response: SVG image or JSON metadata

### Custom Badges

`GET /v2/badge/custom`

Parameters: label, value, style, color, icon, format

### Plugin Badges

`GET /v2/badge/plugin/{plugin}/{metric}`

### Analytics

`GET /api/analytics`

Returns usage statistics.

## Rate Limits

- 100 requests/minute per IP
- Premium tokens available

## Caching

- ETags and Last-Modified headers
- 5-minute TTL