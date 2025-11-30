# Plugins Guide

## Overview

The GitHub Badge API 3.0 supports a plugin system to extend functionality with new badge providers, themes, and effects.

## Creating a Provider Plugin

Create `src/plugins/your_provider.py`:

```python
import httpx

async def get_metric(metric: str) -> str:
    if metric == "followers":
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://api.twitter.com/...")
            return str(resp.json()["followers_count"])
    raise ValueError("Unknown metric")
```

Access via `/v2/badge/plugin/your_provider/followers`

## Built-in Providers

- **github**: GitHub repository stats
- **system**: System load metrics

## Theme Plugins

Plugins can add new themes by modifying `src/themes/__init__.py`.

## Hot Reload

Plugins are loaded on startup. Restart the server to reload changes.

## Security

Plugins run in the same process. Only install trusted plugins.