import importlib
import inspect
from pathlib import Path
from typing import Dict, Callable, Any
import logging

logger = logging.getLogger(__name__)

class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, Callable] = {}
        self.plugin_dir = Path(__file__).parent / "effects"
        self.plugin_dir.mkdir(exist_ok=True)

    def discover_plugins(self):
        """Dynamically load all plugins from the plugins directory"""
        for plugin_file in self.plugin_dir.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue

            try:
                module_name = f"voicechanger.plugins.effects.{plugin_file.stem}"
                module = importlib.import_module(module_name)

                for name, obj in inspect.getmembers(module):
                    if name.startswith("apply_") and inspect.isfunction(obj):
                        effect_name = name.replace("apply_", "")
                        self.plugins[effect_name] = obj
                        logger.info(f"Loaded plugin: {effect_name}")

            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_file}: {e}")

    def get_plugin(self, name: str) -> Callable:
        """Get a plugin by name"""
        if name not in self.plugins:
            raise ValueError(f"Plugin not found: {name}")
        return self.plugins[name]

    def register_plugin(self, name: str, plugin: Callable):
        """Register a new plugin programmatically"""
        self.plugins[name] = plugin
        logger.info(f"Registered plugin: {name}")

    def list_plugins(self) -> Dict[str, Any]:
        """List all available plugins with their metadata"""
        return {
            name: {
                "doc": plugin.__doc__,
                "parameters": inspect.signature(plugin).parameters
            }
            for name, plugin in self.plugins.items()
        }
