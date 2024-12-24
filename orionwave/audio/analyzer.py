import numpy as np
from scipy import signal
import librosa
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class AudioAnalyzer:
    def __init__(self, sample_rate: int, chunk_size: int):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.window = signal.windows.hann(chunk_size)
        self.history_size = 10
        self.history = []

    def analyze_frame(self, frame: np.ndarray) -> Dict[str, float]:
        """Analyze audio frame and return various metrics"""
        # Normalize
        frame = frame.astype(np.float32) / 32768.0
        
        # Calculate RMS
        rms = np.sqrt(np.mean(frame**2))
        
        # Spectral analysis
        freqs, psd = signal.welch(frame, self.sample_rate)
        dominant_freq = freqs[np.argmax(psd)]
        spectral_centroid = np.sum(freqs * psd) / np.sum(psd)
        
        # Pitch detection
        pitches, magnitudes = librosa.piptrack(
            y=frame,
            sr=self.sample_rate,
            n_fft=self.chunk_size
        )
        pitch = np.mean(pitches[magnitudes > np.max(magnitudes)*0.7])

        return {
            'rms': float(rms),
            'dominant_frequency': float(dominant_freq),
            'spectral_centroid': float(spectral_centroid),
            'pitch': float(pitch if not np.isnan(pitch) else 0.0),
            'zero_crossing_rate': float(np.mean(np.abs(np.diff(np.signbit(frame)))))
        }
