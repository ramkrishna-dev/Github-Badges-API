# Plugins Guide

## Overview

The GitHub Badge API 2.0 supports a plugin system to extend badge capabilities beyond GitHub metrics.

## Creating a Plugin

1. Create `plugins/your_plugin.py`
2. Implement `async def get_metric(metric: str) -> str`
3. Return the value as a string

Example:

```python
import httpx

async def get_metric(metric: str) -> str:
    if metric == "followers":
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://api.twitter.com/...")
            return str(resp.json()["followers_count"])
    raise ValueError("Unknown metric")
```

4. Access via `/v2/badge/plugin/your_plugin/followers`

## Built-in Plugins

- **system**: cpu, memory, disk
- Add more in the plugins/ directory

## Security

Plugins run in the same process. Ensure they are trusted.