from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QComboBox, QSlider, QPushButton, QLabel, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QSurfaceFormat
import pyqtgraph as pg
import numpy as np
from ..processor import VoiceProcessor
from ..config import AudioConfig
from .visualizer import AudioVisualizer
import os
import logging

logger = logging.getLogger(__name__)
os.environ['QT_QPA_PLATFORM'] = 'xcb'  # Force xcb backend

# Configure OpenGL format before QApplication
def configure_opengl():
    fmt = QSurfaceFormat()
    fmt.setVersion(2, 1)  # Use OpenGL 2.1
    fmt.setProfile(QSurfaceFormat.NoProfile)
    fmt.setRenderableType(QSurfaceFormat.OpenGL)
    fmt.setDepthBufferSize(24)
    fmt.setStencilBufferSize(8)
    fmt.setSamples(4)
    QSurfaceFormat.setDefaultFormat(fmt)

class VoiceChangerGUI(QMainWindow):
    def __init__(self, use_opengl=False):
        super().__init__()
        self.use_opengl = use_opengl
        self.setWindowTitle("Professional Voice Changer")
        self.setMinimumSize(800, 600)
        
        # Initialize audio processor
        self.config = AudioConfig()
        self.processor = VoiceProcessor(self.config)
        
        # Initialize audio
        self.initialize_audio()
        
        # Setup UI
        self.setup_ui()
        self.setup_visualizer()
        self.setup_connections()
        
        # Update timer for visualizations
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_visualizations)
        self.update_timer.start(50)  # 20 fps

    def initialize_audio(self):
        """Initialize audio with proper device selection"""
        try:
            # Get all available devices
            devices = self.processor.get_available_devices()
            
            # Find default devices
            input_device = None
            output_device = None
            
            # Try to find specific device names first
            default_inputs = ['default', 'pulse', 'alsa', 'mic', 'input']
            default_outputs = ['default', 'pulse', 'alsa', 'speaker', 'output']
            
            for idx, name in devices.items():
                name_lower = name.lower()
                # Check for input devices
                if 'input' in name_lower:
                    for default in default_inputs:
                        if default in name_lower:
                            input_device = idx
                            break
                # Check for output devices
                if 'output' in name_lower:
                    for default in default_outputs:
                        if default in name_lower:
                            output_device = idx
                            break
            
            # If no specific devices found, use first available
            if input_device is None:
                input_device = next((idx for idx, name in devices.items() 
                                   if 'input' in name.lower()), None)
            if output_device is None:
                output_device = next((idx for idx, name in devices.items() 
                                    if 'output' in name.lower()), None)

            logger.info(f"Selected input device: {devices.get(input_device)}")
            logger.info(f"Selected output device: {devices.get(output_device)}")

            # Initialize streams with selected devices
            self.processor.initialize_streams(
                input_device_index=input_device,
                output_device_index=output_device
            )
        except Exception as e:
            logger.error(f"Failed to initialize audio: {e}")
            self.show_error_dialog("Audio Initialization Error",
                                 f"Failed to initialize audio devices: {str(e)}")

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Device selection
        devices_layout = QHBoxLayout()
        self.input_devices = QComboBox()
        self.output_devices = QComboBox()
        self.populate_devices()
        devices_layout.addWidget(QLabel("Input:"))
        devices_layout.addWidget(self.input_devices)
        devices_layout.addWidget(QLabel("Output:"))
        devices_layout.addWidget(self.output_devices)
        layout.addLayout(devices_layout)

        # Effects section
        effects_layout = QHBoxLayout()
        self.effects_combo = QComboBox()
        self.effects_combo.addItems(['pitch_shift', 'robot', 'reverb', 'compressor', 'equalizer'])
        self.effect_params = QSlider(Qt.Horizontal)
        self.effect_params.setRange(0, 100)
        effects_layout.addWidget(self.effects_combo)
        effects_layout.addWidget(self.effect_params)
        layout.addLayout(effects_layout)

        # Preset management
        presets_layout = QHBoxLayout()
        self.preset_combo = QComboBox()
        self.save_preset_btn = QPushButton("Save Preset")
        self.load_preset_btn = QPushButton("Load Preset")
        presets_layout.addWidget(self.preset_combo)
        presets_layout.addWidget(self.save_preset_btn)
        presets_layout.addWidget(self.load_preset_btn)
        layout.addLayout(presets_layout)

        # Visualizer placeholder
        self.visualizer_widget = pg.PlotWidget()
        layout.addWidget(self.visualizer_widget)

        # Performance metrics
        self.metrics_label = QLabel()
        layout.addWidget(self.metrics_label)

        # Recording controls
        record_layout = QHBoxLayout()
        self.record_btn = QPushButton("Start Recording")
        self.stop_btn = QPushButton("Stop")
        record_layout.addWidget(self.record_btn)
        record_layout.addWidget(self.stop_btn)
        layout.addLayout(record_layout)

    def setup_visualizer(self):
        """Setup visualizer with multiple fallback options"""
        try:
            if self.use_opengl:
                # Try hardware acceleration first
                pg.setConfigOption('useOpenGL', True)
                pg.setConfigOption('enableExperimental', True)
            else:
                # Use software rendering
                pg.setConfigOption('useOpenGL', False)
                pg.setConfigOption('antialias', False)
            
            # Basic plot configuration
            self.visualizer_widget.setBackground('k')
            self.visualizer_widget.setDownsampling(mode='peak')
            self.visualizer_widget.setClipToView(True)
            
            # Create visualizer
            self.visualizer = AudioVisualizer(self.visualizer_widget)
            
        except Exception as e:
            logger.warning(f"Failed to initialize visualizer: {e}")
            self.show_error_dialog(
                "Visualization Warning",
                "Running with limited visualization capabilities."
            )
            # Create basic visualizer without OpenGL
            pg.setConfigOption('useOpenGL', False)
            pg.setConfigOption('antialias', False)
            self.visualizer = AudioVisualizer(self.visualizer_widget)

    def setup_connections(self):
        self.effects_combo.currentTextChanged.connect(self.change_effect)
        self.effect_params.valueChanged.connect(self.update_effect_params)
        self.record_btn.clicked.connect(self.toggle_recording)
        self.stop_btn.clicked.connect(self.stop_processing)
        self.save_preset_btn.clicked.connect(self.save_preset)
        self.load_preset_btn.clicked.connect(self.load_preset)

    def populate_devices(self):
        """Populate device selection with proper labels"""
        devices = self.processor.get_available_devices()
        
        self.input_devices.clear()
        self.output_devices.clear()
        
        for idx, name in devices.items():
            if 'Input' in name:
                self.input_devices.addItem(name, idx)
            if 'Output' in name:
                self.output_devices.addItem(name, idx)

    def update_visualizations(self):
        """Update visualizations with error handling"""
        try:
            if hasattr(self.processor, 'audio_buffer') and len(self.processor.audio_buffer) > 0:
                self.visualizer.update_plot(self.processor.audio_buffer)
            
            # Update performance metrics
            stats = self.processor.get_audio_stats()
            if stats:
                self.metrics_label.setText(
                    f"Latency: {stats.get('latency', 0):.2f}ms | "
                    f"CPU: {stats.get('cpu_usage', 0):.1f}% | "
                    f"Memory: {stats.get('memory_usage', {}).get('rss', 0):.1f}MB"
                )
        except Exception as e:
            logger.error(f"Error updating visualizations: {e}")
            # Don't raise the error to keep the GUI running

    def change_effect(self, effect_name):
        self.processor.clear_effects()
        self.processor.add_effect(effect_name)

    def update_effect_params(self, value):
        current_effect = self.effects_combo.currentText()
        params = {'value': value / 100.0}  # Normalize to 0-1
        self.processor.add_effect(current_effect, params)

    def toggle_recording(self):
        if self.record_btn.text() == "Start Recording":
            self.processor.start_recording()
            self.record_btn.setText("Stop Recording")
        else:
            self.processor.stop_recording()
            self.record_btn.setText("Start Recording")

    def stop_processing(self):
        self.processor.cleanup()
        self.close()

    def save_preset(self):
        # Implementation in presets.py
        pass

    def load_preset(self):
        # Implementation in presets.py
        pass

    def show_error_dialog(self, title: str, message: str):
        """Show error dialog to user"""
        QMessageBox.critical(self, title, message)
