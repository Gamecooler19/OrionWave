from typing import Protocol, Dict, Any

class VoiceProcessorProtocol(Protocol):
    """Protocol defining VoiceProcessor interface"""
    def add_effect(self, effect_name: str, params: Dict = None) -> None: ...
    def clear_effects(self) -> None: ...
    def load_preset(self, preset_name: str) -> None: ...
    def get_audio_stats(self) -> Dict[str, Any]: ...
