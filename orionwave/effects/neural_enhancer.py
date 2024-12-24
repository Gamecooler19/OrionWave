import numpy as np
import torch
import torch.nn as nn
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class EnhancementModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv1d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv1d(64, 32, kernel_size=3, padding=1)
        self.conv4 = nn.Conv1d(32, 1, kernel_size=3, padding=1)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.conv1(x))
        x = self.relu(self.conv2(x))
        x = self.relu(self.conv3(x))
        x = self.conv4(x)
        return x

class NeuralEnhancer:
    def __init__(self, model_path: Optional[str] = None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = EnhancementModel().to(self.device)
        if model_path:
            self._load_model(model_path)
        self.initialized = True
        self.buffer_size = 2048  # Fixed buffer size for processing
        self.enabled = True

    def _load_model(self, model_path: str):
        try:
            state_dict = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            self.model.eval()
            logger.info(f"Loaded neural enhancement model from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.initialized = False

    @torch.no_grad()
    def enhance(self, audio_data: np.ndarray) -> np.ndarray:
        """Enhance audio with error handling and proper array copying"""
        if not self.initialized or not self.enabled:
            return audio_data

        try:
            # Make a writable copy of the input array
            audio_copy = np.array(audio_data, dtype=np.float32, copy=True) / 32768.0
            
            # Pad or truncate to fixed buffer size
            if len(audio_copy) < self.buffer_size:
                audio_copy = np.pad(audio_copy, (0, self.buffer_size - len(audio_copy)))
            elif len(audio_copy) > self.buffer_size:
                audio_copy = audio_copy[:self.buffer_size]
            
            # Convert to tensor
            audio_tensor = torch.from_numpy(audio_copy).to(self.device)
            audio_tensor = audio_tensor.unsqueeze(0).unsqueeze(0)
            
            # Process through model
            with torch.inference_mode():
                enhanced = self.model(audio_tensor)
            
            # Convert back to numpy and original length
            result = enhanced.squeeze().cpu().numpy()
            result = result[:len(audio_data)]  # Truncate to original length
            
            # Scale and convert to int16
            result = np.clip(result * 32768.0, -32768, 32767).astype(np.int16)
            
            return result
            
        except Exception as e:
            logger.error(f"Neural enhancement failed: {e}")
            self.enabled = False  # Disable enhancement on error
            return audio_data
