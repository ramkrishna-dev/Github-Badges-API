import importlib
import os
from typing import Dict, Callable

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

def get_plugin_metric(plugin: str, metric: str):
    if plugin in PLUGINS:
        return PLUGINS[plugin](metric)
    raise ValueError(f"Plugin {plugin} not found")

def list_plugins():
    return list(PLUGINS.keys())