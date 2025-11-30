import httpx
from typing import Optional, Dict, Any

async def fetch_pypi_data(package: str) -> Dict[str, Any]:
    url = f'https://pypi.org/pypi/{package}/json'
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

async def get_pypi_metric(package: str, metric: str) -> str:
    data = await fetch_pypi_data(package)
    info = data.get('info', {})

    if metric == 'downloads':
        # PyPI doesn't provide download counts easily, return version for now
        return info.get('version', 'unknown')
    elif metric == 'version':
        return info.get('version', 'unknown')
    else:
        raise ValueError(f'Unknown metric: {metric}')