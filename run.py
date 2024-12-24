#!/usr/bin/env python3
import sys
import logging
import warnings
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import os

# Set environment variables before importing Qt modules
os.environ['QT_QPA_PLATFORM'] = 'xcb'  # Use xcb backend
os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'  # Reduce Qt logging
os.environ['QT_XCB_GL_INTEGRATION'] = 'none'  # Disable default GL integration

from orionwave import AudioConfig
from orionwave.gui.main_window import VoiceChangerGUI, configure_opengl

def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('orionwave.log')
        ]
    )

def load_config():
    """Load configuration"""
    config_path = Path('config.yaml')
    if config_path.exists():
        return AudioConfig.from_yaml(str(config_path))
    return AudioConfig()

def setup_qt_graphics():
    """Configure Qt graphics settings"""
    try:
        # Try software rendering first
        QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)
    except:
        # If that fails, try system default
        QApplication.setAttribute(Qt.AA_UseDesktopOpenGL)
    
    # Disable problematic features
    QApplication.setAttribute(Qt.AA_DisableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

def main():
    # Suppress warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    warnings.filterwarnings("ignore", message="path is deprecated")

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Setup Qt graphics before creating QApplication
        setup_qt_graphics()
        
        # Initialize Qt Application
        app = QApplication(sys.argv)
        
        # Configure OpenGL
        configure_opengl()
        
        # Load configuration
        logger.info("Loading configuration...")
        config = load_config()
        
        # Create and show main window
        logger.info("Initializing GUI...")
        window = VoiceChangerGUI(use_opengl=False)  # Disable OpenGL by default
        window.show()
        
        # Run application
        logger.info("OrionWave GUI started")
        return app.exec_()
        
    except Exception as e:
        logger.error(f"Failed to start OrionWave: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
