import numpy as np
from scipy import signal
import warnings
from typing import Dict, Any

# Suppress warnings
warnings.filterwarnings("ignore", message="path is deprecated")

def apply_pitch_shift(data: np.ndarray, config: Any, shift: int = 200) -> np.ndarray:
    """Apply pitch shifting to audio data"""
    try:
        import librosa
        return _apply_pitch_shift_librosa(data, config, shift)
    except ImportError:
        return _apply_pitch_shift_basic(data, config, shift)

def _apply_pitch_shift_librosa(data: np.ndarray, config: Any, shift: int) -> np.ndarray:
    """Pitch shift using librosa if available"""
    # Store original length
    original_length = len(data)
    
    try:
        # Convert to float32 for processing
        audio_float = data.astype(np.float32) / 32768.0
        
        # Apply pitch shift
        shifted = librosa.effects.pitch_shift(
            audio_float,
            sr=config.RATE,
            n_steps=shift/100,
            res_type='kaiser_fast'
        )
        
        # Ensure output length matches input length
        if len(shifted) > original_length:
            shifted = shifted[:original_length]
        elif len(shifted) < original_length:
            shifted = np.pad(shifted, (0, original_length - len(shifted)))
        
        return np.clip(shifted * 32768.0, -32768, 32767).astype(np.int16)
    except Exception as e:
        warnings.warn(f"Librosa pitch shift failed: {e}, falling back to basic method")
        return _apply_pitch_shift_basic(data, config, shift)

def _apply_pitch_shift_basic(data: np.ndarray, config: Any, shift: int) -> np.ndarray:
    """Basic pitch shift using FFT"""
    # Perform FFT
    fft = np.fft.rfft(data)
    
    # Shift frequencies
    shifted = np.roll(fft, shift)
    if shift > 0:
        shifted[:shift] = 0
    else:
        shifted[shift:] = 0
        
    # Inverse FFT
    result = np.fft.irfft(shifted)
    
    # Ensure same length as input
    if len(result) > len(data):
        result = result[:len(data)]
    elif len(result) < len(data):
        result = np.pad(result, (0, len(data) - len(result)))
    
    return result.astype(np.int16)

def apply_robot_effect(data: np.ndarray, config: Any, frequency: float = 50) -> np.ndarray:
    """Apply robot-like modulation effect"""
    t = np.arange(len(data)) / config.RATE
    carrier = np.sin(2 * np.pi * frequency * t)
    # Ensure modulation has an effect
    modulated = (data.astype(np.float32) * (0.5 + 0.5 * carrier))
    return np.clip(modulated, -32768, 32767).astype(np.int16)

def apply_reverb(data: np.ndarray, config: Any, room_size: float = 0.8) -> np.ndarray:
    """Apply reverb effect"""
    reverb_time = int(room_size * config.RATE)
    impulse_response = np.exp(-3 * np.arange(reverb_time) / reverb_time)
    reverbed = signal.convolve(data, impulse_response, mode='same')
    return (reverbed * 0.6).astype(np.int16)

def apply_compression(data: np.ndarray, config: Any, threshold: float = 0.5, ratio: float = 4.0) -> np.ndarray:
    """Apply dynamic range compression"""
    data_float = data.astype(np.float32) / 32768.0
    mask = np.abs(data_float) > threshold
    data_float[mask] = (threshold + (np.abs(data_float[mask]) - threshold) / ratio) * np.sign(data_float[mask])
    return (data_float * 32768).astype(np.int16)

def apply_eq(data: np.ndarray, config: Any, bands: Dict[str, float] = None) -> np.ndarray:
    """Apply three-band equalizer"""
    if bands is None:
        bands = {'low': 1.0, 'mid': 1.0, 'high': 1.0}
    
    nyquist = config.RATE // 2
    low_cut, mid_cut = 200, 2000
    
    b1, a1 = signal.butter(2, low_cut/nyquist, btype='lowpass')
    b2, a2 = signal.butter(2, [low_cut/nyquist, mid_cut/nyquist], btype='bandpass')
    b3, a3 = signal.butter(2, mid_cut/nyquist, btype='highpass')

    low = signal.filtfilt(b1, a1, data) * bands['low']
    mid = signal.filtfilt(b2, a2, data) * bands['mid']
    high = signal.filtfilt(b3, a3, data) * bands['high']

    return (low + mid + high).astype(np.int16)
