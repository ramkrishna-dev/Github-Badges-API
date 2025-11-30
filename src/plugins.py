import importlib
import os
from typing import Dict, Any, Callable

PLUGINS: Dict[str, Callable] = {}

def load_plugins():
    plugin_dir = "plugins"
    if not os.path.exists(plugin_dir):
        return
    for file in os.listdir(plugin_dir):
        if file.endswith(".py") and not file.startswith("__"):
            module_name = file[:-3]
            try:
                module = importlib.import_module(f"plugins.{module_name}")
                if hasattr(module, "get_metric"):
                    PLUGINS[module_name] = module.get_metric
            except ImportError:
                pass

async def get_plugin_metric(plugin: str, metric: str) -> str:
    if plugin in PLUGINS:
        return await PLUGINS[plugin](metric)
    raise ValueError(f"Plugin {plugin} not found")