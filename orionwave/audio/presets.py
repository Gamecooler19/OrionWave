import json
from pathlib import Path
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class PresetManager:
    def __init__(self):
        self.presets_dir = Path("presets")
        self.presets_dir.mkdir(exist_ok=True)
        self.current_preset = None
        self._load_default_presets()

    def _load_default_presets(self):
        """Initialize default presets"""
        defaults = {
            "natural": {
                "effects": [
                    ("eq", {"low": 1.1, "mid": 1.0, "high": 1.05})
                ]
            },
            "robot": {
                "effects": [
                    ("robot", {"frequency": 50}),
                    ("reverb", {"room_size": 0.8})
                ]
            },
            "high_pitch": {
                "effects": [
                    ("pitch_shift", {"shift": 300}),
                    ("compression", {"threshold": 0.5})
                ]
            }
        }
        
        for name, preset in defaults.items():
            self.save_preset(name, preset)

    def save_preset(self, name: str, settings: Dict[str, Any]) -> bool:
        """Save a preset to file"""
        try:
            path = self.presets_dir / f"{name}.json"
            with open(path, 'w') as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save preset {name}: {e}")
            return False

    def load_preset(self, name: str) -> Dict[str, Any]:
        """Load a preset from file"""
        try:
            path = self.presets_dir / f"{name}.json"
            with open(path, 'r') as f:
                preset = json.load(f)
            self.current_preset = name
            return preset
        except Exception as e:
            logger.error(f"Failed to load preset {name}: {e}")
            return None

    def list_presets(self) -> List[str]:
        """Get list of available presets"""
        return [p.stem for p in self.presets_dir.glob("*.json")]
