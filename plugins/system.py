import psutil
import asyncio

async def get_metric(metric: str) -> str:
    if metric == "cpu":
        return f"{psutil.cpu_percent()}%"
    elif metric == "memory":
        return f"{psutil.virtual_memory().percent}%"
    elif metric == "disk":
        return f"{psutil.disk_usage('/').percent}%"
    else:
        raise ValueError(f"Unknown metric: {metric}")