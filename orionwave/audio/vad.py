import numpy as np
from scipy import signal
import logging

logger = logging.getLogger(__name__)

class VoiceActivityDetector:
    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate
        self.energy_threshold = 0.1
        self.freq_threshold = 0.2
        self.history_size = 10
        self.energy_history = []

    def is_speech(self, frame: np.ndarray) -> bool:
        """Detect if frame contains speech"""
        # Normalize
        frame = frame.astype(float) / np.iinfo(np.int16).max
        
        # Energy detection
        energy = np.sum(frame ** 2) / len(frame)
        self.energy_history.append(energy)
        if len(self.energy_history) > self.history_size:
            self.energy_history.pop(0)
        
        # Frequency analysis
        freqs, psd = signal.welch(frame, self.sample_rate)
        dom_freq = freqs[np.argmax(psd)]
        
        # Combined decision
        is_active = (
            energy > np.mean(self.energy_history) * self.energy_threshold and
            50 < dom_freq < 400
        )
        
        return is_active
