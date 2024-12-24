import wave
import threading
import numpy as np
import soundfile as sf
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class RecordingManager:
    def __init__(self, config):
        self.config = config
        self.recording = False
        self.buffer: List[np.ndarray] = []
        self._lock = threading.Lock()
        self.output_dir = Path("recordings")
        self.output_dir.mkdir(exist_ok=True)

    def start_recording(self):
        with self._lock:
            self.recording = True
            self.buffer.clear()
        logger.info("Started recording")

    def stop_recording(self) -> Optional[str]:
        with self._lock:
            self.recording = False
            if not self.buffer:
                return None
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"recording_{timestamp}.wav"
            
            try:
                audio_data = np.concatenate(self.buffer)
                sf.write(
                    output_path,
                    audio_data,
                    self.config.RATE,
                    subtype='PCM_16'
                )
                logger.info(f"Saved recording to {output_path}")
                return str(output_path)
            except Exception as e:
                logger.error(f"Failed to save recording: {e}")
                return None
            finally:
                self.buffer.clear()

    def add_audio(self, audio_data: np.ndarray):
        if self.recording:
            with self._lock:
                self.buffer.append(audio_data.copy())

    def convert_format(self, input_path: str, output_format: str = 'mp3'):
        try:
            data, sample_rate = sf.read(input_path)
            output_path = str(Path(input_path).with_suffix(f'.{output_format}'))
            sf.write(output_path, data, sample_rate)
            logger.info(f"Converted audio to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Format conversion failed: {e}")
            return None
