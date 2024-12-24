import numpy as np
from scipy import signal
import logging
from typing import Tuple, List, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class VisualizationData:
    spectrum: np.ndarray
    frequencies: np.ndarray
    waveform: np.ndarray
    peak_frequencies: List[float]
    rms_level: float

class SpectrumAnalyzer:
    def __init__(self, sample_rate: int, chunk_size: int):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.window = signal.windows.hann(chunk_size)
        self.smoothing_factor = 0.7
        self.previous_spectrum = None
        
    def analyze(self, audio_data: np.ndarray) -> VisualizationData:
        """Analyze audio frame for visualization"""
        # Normalize audio
        audio_normalized = audio_data.astype(np.float32) / 32768.0
        
        # Calculate spectrum
        frequencies, times, spectogram = signal.spectrogram(
            audio_normalized,
            fs=self.sample_rate,
            window=self.window,
            nperseg=self.chunk_size,
            noverlap=self.chunk_size // 2,
            scaling='spectrum'
        )

        # Get current spectrum
        current_spectrum = np.mean(spectogram, axis=1)
        
        # Apply smoothing
        if self.previous_spectrum is not None:
            current_spectrum = (self.smoothing_factor * self.previous_spectrum + 
                              (1 - self.smoothing_factor) * current_spectrum)
        self.previous_spectrum = current_spectrum

        # Find peak frequencies
        peak_indices = signal.find_peaks(current_spectrum)[0]
        peak_frequencies = frequencies[peak_indices]

        # Calculate RMS level
        rms_level = np.sqrt(np.mean(audio_normalized**2))

        return VisualizationData(
            spectrum=current_spectrum,
            frequencies=frequencies,
            waveform=audio_normalized,
            peak_frequencies=peak_frequencies.tolist(),
            rms_level=float(rms_level)
        )

    def get_frequency_bands(self, spectrum: np.ndarray) -> Dict[str, float]:
        """Calculate energy in different frequency bands"""
        freq_bands = {
            'sub_bass': (20, 60),
            'bass': (60, 250),
            'low_mid': (250, 500),
            'mid': (500, 2000),
            'upper_mid': (2000, 4000),
            'presence': (4000, 6000),
            'brilliance': (6000, 20000)
        }

        bands_energy = {}
        freq_resolution = self.sample_rate / self.chunk_size

        for band_name, (low, high) in freq_bands.items():
            low_idx = int(low / freq_resolution)
            high_idx = int(high / freq_resolution)
            bands_energy[band_name] = np.mean(spectrum[low_idx:high_idx])

        return bands_energy
