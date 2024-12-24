import numpy as np
import pyaudio
import logging
import time
import threading
from typing import Optional, Dict, Callable
from .config import AudioConfig
from .effects import (
    apply_pitch_shift, 
    apply_robot_effect,
    apply_reverb, 
    apply_compression, 
    apply_eq
)
from .plugins.plugin_manager import PluginManager
from .monitoring import PerformanceMonitor
from .recording import RecordingManager
from .audio.noise_reduction import NoiseReducer  # Updated import path
from .audio.vad import VoiceActivityDetector
from .audio.presets import PresetManager
from .audio.enhancer import AudioEnhancer
from .audio.analyzer import AudioAnalyzer
from .automation import ParameterAutomation
from .visualization.spectrum_analyzer import SpectrumAnalyzer
from .effects.neural_enhancer import NeuralEnhancer
from .audio.routing import AudioRouter
import asyncio

# Add ALSA error handling
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

try:
    import sounddevice as sd
    sd._initialize()
except Exception as e:
    logger.warning(f"Audio initialization warning: {e}")

try:
    from .audio.plugins.vst_wrapper import VSTPlugin
except ImportError:
    logger.warning("VST support not available")
    VSTPlugin = None

logger = logging.getLogger(__name__)

class VoiceProcessor:
    def __init__(self, config: AudioConfig, start_server: bool = False):
        try:
            self.pyaudio = pyaudio.PyAudio()
        except Exception as e:
            logger.warning(f"PyAudio initialization warning: {e}")
            self.pyaudio = None
        self.config = config
        self.input_stream = None
        self.output_stream = None
        self.monitor = PerformanceMonitor()
        self.effects_chain = []
        self.audio_buffer = np.array([], dtype=np.int16)
        self.setup_effects_chain()
        self.recording_manager = RecordingManager(config)
        self.plugin_manager = PluginManager()
        self.plugin_manager.discover_plugins()
        self.noise_reducer = NoiseReducer(config.RATE)
        self.vad = VoiceActivityDetector(config.RATE)
        self.preset_manager = PresetManager()
        self.enhancer = AudioEnhancer(config.RATE)
        self.analyzer = AudioAnalyzer(config.RATE, config.CHUNK)
        self.automation = ParameterAutomation()
        self.analysis_results = {}
        self.voice_active = False
        self.spectrum_analyzer = SpectrumAnalyzer(config.RATE, config.CHUNK)
        self.visualization_data = None
        self.router = AudioRouter()
        self.neural_enhancer = NeuralEnhancer()
        self.vst_plugins = {}
        self.recording_active = False
        self._setup_routing()
        self._load_vst_plugins()
        self._initialize_server() if start_server else None

    def _initialize_server(self):
        """Initialize WebSocket server separately to avoid circular imports"""
        from .network.websocket_server import VoiceChangerServer
        self.server = VoiceChangerServer(self)
        self._start_server()

    def get_available_devices(self) -> Dict[int, str]:
        """Get available audio devices with better detection"""
        devices = {}
        try:
            default_input = self.pyaudio.get_default_input_device_info()
            default_output = self.pyaudio.get_default_output_device_info()
            
            for i in range(self.pyaudio.get_device_count()):
                try:
                    device_info = self.pyaudio.get_device_info_by_index(i)
                    
                    # Check if device is working
                    if device_info.get('maxInputChannels', 0) > 0:
                        name = device_info.get('name', '')
                        if i == default_input['index']:
                            name = f"Input: {name} (Default)"
                        else:
                            name = f"Input: {name}"
                        devices[i] = name
                        
                    if device_info.get('maxOutputChannels', 0) > 0:
                        name = device_info.get('name', '')
                        if i == default_output['index']:
                            name = f"Output: {name} (Default)"
                        else:
                            name = f"Output: {name}"
                        devices[i] = name
                        
                except Exception as e:
                    logger.debug(f"Skipping device {i}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error enumerating audio devices: {e}")
            
        if not devices:
            # Fallback to default devices
            devices[-1] = "Input: Default System Input"
            devices[-2] = "Output: Default System Output"
            
        return devices

    def setup_effects_chain(self):
        self.effects_registry = {
            'pitch_shift': apply_pitch_shift,
            'robot': apply_robot_effect,
            'reverb': apply_reverb,
            'compressor': apply_compression,
            'equalizer': apply_eq
        }

    def initialize_streams(self, input_device_index=None, output_device_index=None):
        try:
            self.input_stream = self.pyaudio.open(
                format=self.pyaudio.get_format_from_width(self.config.FORMAT // 8),
                channels=self.config.CHANNELS,
                rate=self.config.RATE,
                input=True,
                input_device_index=input_device_index,
                frames_per_buffer=self.config.CHUNK,
                stream_callback=self._audio_callback
            )
            
            self.output_stream = self.pyaudio.open(
                format=self.pyaudio.get_format_from_width(self.config.FORMAT // 8),
                channels=self.config.CHANNELS,
                rate=self.config.RATE,
                output=True,
                output_device_index=output_device_index,
                frames_per_buffer=self.config.CHUNK
            )
            
            logger.info("Audio streams initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize audio streams: {e}")
            raise

    def calibrate_noise_reduction(self, duration: float = 2.0):
        """Calibrate noise reduction using ambient noise"""
        logger.info("Calibrating noise reduction...")
        frames = []
        for _ in range(int(duration * self.config.RATE / self.config.CHUNK)):
            data = self.input_stream.read(self.config.CHUNK)
            frames.append(np.frombuffer(data, dtype=np.int16))
        noise_sample = np.concatenate(frames)
        self.noise_reducer.calibrate(noise_sample)

    def _audio_callback(self, in_data, frame_count, time_info, status):
        with self.monitor.measure_performance("audio_processing"):
            try:
                audio_data = np.frombuffer(in_data, dtype=np.int16)
                processed_data = audio_data  # Default to unprocessed audio
                
                # Safe analysis
                try:
                    self.visualization_data = self.spectrum_analyzer.analyze(audio_data)
                    self.analysis_results = self.analyzer.analyze_frame(audio_data)
                    
                    # Use safe get() for dict access
                    rms = self.analysis_results.get('rms', 0)
                    self.voice_active = self.vad.is_speech(audio_data) and rms > 0.1
                except Exception as e:
                    logger.error(f"Analysis error: {e}")
                    self.voice_active = True  # Default to active on error
                
                if self.voice_active:
                    try:
                        # Neural enhancement with error check
                        if hasattr(self.neural_enhancer, 'enabled') and self.neural_enhancer.enabled:
                            audio_data = self.neural_enhancer.enhance(audio_data)
                        
                        # Rest of processing chain
                        if self.noise_reducer.initialized:
                            audio_data = self.noise_reducer.process(audio_data)
                        
                        self._adapt_effects_to_audio()
                        processed_data = self.process_effects_chain(audio_data)
                        processed_data = self.enhancer.process(processed_data)
                        
                        if self.recording_active:
                            self.recording_manager.add_audio(processed_data)
                    except Exception as e:
                        logger.error(f"Processing error: {e}")
                        processed_data = audio_data  # Use original audio on error

                return (processed_data.tobytes(), pyaudio.paContinue)
                
            except Exception as e:
                logger.error(f"Critical error in audio callback: {e}")
                return (in_data, pyaudio.paAbort)

    def process_effects_chain(self, audio_data: np.ndarray) -> np.ndarray:
        processed_data = audio_data
        for effect, params in self.effects_chain:
            with self.monitor.measure_performance(f"effect_{effect}"):
                effect_func = self.effects_registry.get(effect)
                if effect_func:
                    # Handle legacy filter types
                    if effect == 'equalizer' and 'type' in params:
                        if params['type'] == 'highshelf':
                            params['type'] = 'high_shelf'
                        elif params['type'] == 'lowshelf':
                            params['type'] = 'low_shelf'
                    processed_data = effect_func(processed_data, self.config, **params)
        return processed_data

    def add_effect(self, effect_name: str, params: Dict = None):
        if effect_name in self.effects_registry:
            self.effects_chain.append((effect_name, params or {}))
            logger.info(f"Added effect: {effect_name} with params: {params}")
        else:
            raise ValueError(f"Unknown effect: {effect_name}")

    def clear_effects(self):
        self.effects_chain.clear()
        logger.info("Effects chain cleared")

    def load_preset(self, preset_name: str):
        """Load and apply an effect preset"""
        preset = self.preset_manager.load_preset(preset_name)
        if preset:
            self.clear_effects()
            for effect, params in preset['effects']:
                self.add_effect(effect, params)
            logger.info(f"Applied preset: {preset_name}")

    def get_audio_stats(self) -> Dict:
        """Get current audio processing statistics"""
        stats = {
            'latency': self.monitor.get_average_time("audio_processing"),
            'effects_timing': self.monitor.get_all_timings(),
            'cpu_usage': self.monitor.get_cpu_usage(),
            'memory_usage': self.monitor.get_memory_usage(),
            'analysis': self.analysis_results,
            'voice_active': self.voice_active
        }
        
        if self.visualization_data:
            stats.update({
                'visualization': {
                    'spectrum': self.visualization_data.spectrum.tolist(),
                    'peak_frequencies': self.visualization_data.peak_frequencies,
                    'rms_level': self.visualization_data.rms_level,
                    'frequency_bands': self.spectrum_analyzer.get_frequency_bands(
                        self.visualization_data.spectrum
                    )
                }
            })
        return stats

    def _adapt_effects_to_audio(self):
        """Adapt effect parameters with error handling"""
        try:
            if not self.analysis_results:
                return

            clarity = self.analysis_results.get('clarity', 0.5)  # Default value if missing
            rms = self.analysis_results.get('rms', 0.0)  # Default value if missing

            if 'reverb' in self.effects_registry:
                self.automation.add_automation(
                    'reverb_mix',
                    start_value=0.5,
                    end_value=0.3 + (0.6 * clarity),
                    duration=0.2,
                    callback=lambda name, value: self._update_effect_param('reverb', 'mix', value)
                )

            if 'compressor' in self.effects_registry:
                threshold = -20 + (rms * 10)
                self._update_effect_param('compressor', 'threshold', threshold)
                
        except Exception as e:
            logger.error(f"Error in effects adaptation: {e}")

    def _update_effect_param(self, effect: str, param: str, value: float):
        """Update a specific effect parameter"""
        for i, (eff_name, params) in enumerate(self.effects_chain):
            if eff_name == effect:
                self.effects_chain[i][1][param] = value
                break

    def cleanup(self):
        logger.info("Cleaning up audio streams")
        for stream in [self.input_stream, self.output_stream]:
            if stream:
                stream.stop_stream()
                stream.close()
        self.pyaudio.terminate()
        self.monitor.save_statistics()
        asyncio.get_event_loop().stop()

    def _start_server(self):
        """Start WebSocket server in background"""
        self.server_thread = threading.Thread(target=self._run_server)
        self.server_thread.daemon = True
        self.server_thread.start()

    def _run_server(self):
        """Run WebSocket server in event loop"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.server.start())
        except Exception as e:
            logger.error(f"Server error: {e}")
            # Don't raise, allow program to continue without server

    def _setup_routing(self):
        """Initialize audio routing"""
        self.router.add_route('input', 'main_out')
        self.router.add_route('input', 'monitor', volume=0.5)
        logger.info("Audio routing initialized")

    def _load_vst_plugins(self):
        """Load VST plugins from config"""
        if not VSTPlugin:
            logger.warning("VST plugins not supported")
            return
            
        if self.config.EFFECTS and 'vst_plugins' in self.config.EFFECTS:
            for plugin_path in self.config.EFFECTS['vst_plugins']:
                try:
                    plugin = VSTPlugin(plugin_path, self.config.RATE)
                    self.vst_plugins[plugin_path] = plugin
                except Exception as e:
                    logger.error(f"Failed to load VST plugin {plugin_path}: {e}")

    def pitch_shift(self, data: bytes, shift: int) -> bytes:
        """Legacy method for pitch shift effect"""
        audio_data = np.frombuffer(data, dtype=np.int16)
        processed = apply_pitch_shift(audio_data, self.config, shift=shift)
        return processed.tobytes()

    def robot_effect(self, data: bytes) -> bytes:
        """Legacy method for robot effect"""
        audio_data = np.frombuffer(data, dtype=np.int16)
        processed = apply_robot_effect(audio_data, self.config)
        return processed.tobytes()

    def start_recording(self):
        """Start audio recording"""
        if not self.recording_active:
            self.recording_active = True
            self.recording_manager.start_recording()
            logger.info("Started recording")

    def stop_recording(self) -> Optional[str]:
        """Stop audio recording and return file path"""
        if self.recording_active:
            self.recording_active = False
            return self.recording_manager.stop_recording()
        return None

class AudioProcessor:
    VALID_FILTER_TYPES = [
        'lowpass', 'highpass', 'bandpass', 'notch',
        'low_shelf', 'high_shelf', 'peaking'  # Ensure high_shelf is listed
    ]
