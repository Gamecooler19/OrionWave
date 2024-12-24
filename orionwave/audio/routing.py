import numpy as np
from typing import Dict, List, Optional
import sounddevice as sd
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AudioRoute:
    source: str
    destination: str
    active: bool = True
    volume: float = 1.0
    pan: float = 0.0  # -1 to 1

class AudioRouter:
    def __init__(self):
        self.routes: List[AudioRoute] = []
        self.virtual_channels: Dict[str, np.ndarray] = {}
        self._initialize_virtual_channels()

    def _initialize_virtual_channels(self):
        """Initialize default virtual channels"""
        default_channels = ['main_out', 'aux_1', 'aux_2', 'monitor']
        for channel in default_channels:
            self.virtual_channels[channel] = np.array([], dtype=np.float32)

    def add_route(self, source: str, destination: str, volume: float = 1.0):
        """Add a new audio route"""
        route = AudioRoute(source=source, destination=destination, volume=volume)
        self.routes.append(route)
        logger.info(f"Added route: {source} -> {destination}")

    def remove_route(self, source: str, destination: str):
        """Remove an existing route"""
        self.routes = [r for r in self.routes 
                      if not (r.source == source and r.destination == destination)]
        logger.info(f"Removed route: {source} -> {destination}")

    def process_routing(self, audio_data: np.ndarray, source: str) -> Dict[str, np.ndarray]:
        """Process audio through routing matrix"""
        output_buffers = {}
        
        # Normalize audio
        audio_float = audio_data.astype(np.float32) / 32768.0

        # Route audio to destinations
        for route in self.routes:
            if route.source == source and route.active:
                # Apply volume and pan
                processed = audio_float * route.volume
                if route.pan != 0:
                    processed = self._apply_panning(processed, route.pan)
                
                if route.destination not in output_buffers:
                    output_buffers[route.destination] = processed
                else:
                    output_buffers[route.destination] += processed

        # Convert back to int16 for output
        for dest in output_buffers:
            output_buffers[dest] = np.clip(output_buffers[dest] * 32768.0, 
                                         -32768, 32767).astype(np.int16)

        return output_buffers

    def _apply_panning(self, audio: np.ndarray, pan: float) -> np.ndarray:
        """Apply panning to mono audio signal"""
        if len(audio.shape) > 1 and audio.shape[1] == 2:
            return audio  # Already stereo

        left_gain = np.sqrt(2) * np.cos(pan * np.pi / 4)
        right_gain = np.sqrt(2) * np.sin(pan * np.pi / 4)
        
        stereo = np.vstack((audio * left_gain, audio * right_gain)).T
        return stereo
