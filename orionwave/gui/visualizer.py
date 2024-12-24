import numpy as np
import pyqtgraph as pg
from scipy import fftpack
import logging

logger = logging.getLogger(__name__)

class AudioVisualizer:
    def __init__(self, plot_widget):
        self.plot_widget = plot_widget
        self.setup_basic_plot()
        self.setup_performance_options()

    def setup_basic_plot(self):
        """Setup basic plotting with minimal features"""
        # Basic configuration
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setMouseEnabled(x=False, y=False)
        
        # Create simple line plots
        self.waveform_plot = self.plot_widget.plot(
            pen=pg.mkPen('g', width=1),
            name='Waveform'
        )
        
        # Reduce update frequency
        self.update_counter = 0
        self.update_skip = 3  # Update every N frames

    def setup_performance_options(self):
        """Configure for better performance"""
        self.plot_widget.setDownsampling(ds=True, auto=True, mode='peak')
        self.plot_widget.setClipToView(True)
        self.max_points = 1000  # Maximum points to display

    def update_plot(self, audio_data: np.ndarray):
        """Update plot with performance optimizations"""
        self.update_counter += 1
        if self.update_counter % self.update_skip != 0:
            return

        try:
            # Downsample data for display
            if len(audio_data) > self.max_points:
                step = len(audio_data) // self.max_points
                display_data = audio_data[::step]
            else:
                display_data = audio_data

            # Update plot
            self.waveform_plot.setData(display_data)
            
        except Exception as e:
            logger.error(f"Error updating plot: {e}")
