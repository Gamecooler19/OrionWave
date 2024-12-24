import numpy as np
from scipy import signal
from typing import Dict, Any
import librosa

def apply_pitch_shift(data: np.ndarray, config: Any, shift: int = 200) -> np.ndarray:
    return librosa.effects.pitch_shift(
        data.astype(np.float32),
        sr=config.RATE,
        n_steps=shift/100
    ).astype(np.int16)

def apply_robot_effect(data: np.ndarray, config: Any, frequency: float = 50) -> np.ndarray:
    t = np.arange(len(data)) / config.RATE
    carrier = np.sin(2 * np.pi * frequency * t)
    modulated = data.astype(np.float32) * carrier
    return (modulated * 0.8).astype(np.int16)

def apply_reverb(data: np.ndarray, config: Any, room_size: float = 0.8) -> np.ndarray:
    # Simple convolution reverb
    reverb_time = int(room_size * config.RATE)
    impulse_response = np.exp(-3 * np.arange(reverb_time) / reverb_time)
    reverbed = signal.convolve(data, impulse_response, mode='same')
    return (reverbed * 0.6).astype(np.int16)

def apply_compression(data: np.ndarray, config: Any, threshold: float = 0.5, ratio: float = 4.0) -> np.ndarray:
    # Dynamic range compression
    data_float = data.astype(np.float32) / 32768.0
    mask = np.abs(data_float) > threshold
    data_float[mask] = (
        threshold + (np.abs(data_float[mask]) - threshold) / ratio
    ) * np.sign(data_float[mask])
    return (data_float * 32768).astype(np.int16)

def apply_eq(data: np.ndarray, config: Any, bands: Dict[str, float] = None) -> np.ndarray:
    if bands is None:
        bands = {'low': 1.0, 'mid': 1.0, 'high': 1.0}
    
    # Three-band equalizer
    nyquist = config.RATE // 2
    low_cut = 200
    mid_cut = 2000

    # Design filters
    b1, a1 = signal.butter(2, low_cut/nyquist, btype='lowpass')
    b2, a2 = signal.butter(2, [low_cut/nyquist, mid_cut/nyquist], btype='bandpass')
    b3, a3 = signal.butter(2, mid_cut/nyquist, btype='highpass')

    # Apply filters
    low = signal.filtfilt(b1, a1, data) * bands['low']
    mid = signal.filtfilt(b2, a2, data) * bands['mid']
    high = signal.filtfilt(b3, a3, data) * bands['high']

    return (low + mid + high).astype(np.int16)
