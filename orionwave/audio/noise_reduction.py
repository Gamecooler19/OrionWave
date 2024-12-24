import numpy as np
import librosa
import logging

logger = logging.getLogger(__name__)

class NoiseReducer:
    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate
        self.noise_profile = None
        self.initialized = False

    def calibrate(self, noise_sample: np.ndarray):
        """Calibrate noise reduction using a sample of background noise"""
        self.noise_profile = np.mean(np.abs(librosa.stft(noise_sample)), axis=1)
        self.initialized = True
        logger.info("Noise profile calibrated")

    def process(self, audio_data: np.ndarray) -> np.ndarray:
        if not self.initialized:
            return audio_data

        # Compute STFT
        stft = librosa.stft(audio_data)
        mag = np.abs(stft)
        phase = np.angle(stft)

        # Apply noise reduction
        mag = np.maximum(0, mag - self.noise_profile[:, np.newaxis])
        
        # Reconstruct signal
        cleaned = librosa.istft(mag * np.exp(1j * phase))
        return cleaned.astype(np.int16)
