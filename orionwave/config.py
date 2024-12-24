import yaml
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class AudioConfig:
    CHUNK: int = 1024
    FORMAT: int = 16
    CHANNELS: int = 1
    RATE: int = 44100
    EFFECTS: Dict[str, Any] = None

    @classmethod
    def from_yaml(cls, file_path: str) -> 'AudioConfig':
        with open(file_path, 'r') as f:
            config_data = yaml.safe_load(f)
        return cls(**config_data)
