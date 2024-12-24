# Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- PortAudio (for audio I/O)
- CUDA (optional, for ML features)

## Basic Installation

```bash
pip install orionwave
```

## Feature-Specific Installation

OrionWave offers multiple installation options depending on your needs:

### GUI Support
```bash
pip install 'orionwave[gui]'
```
- Includes PyQt5 and visualization components

### Audio Processing
```bash
pip install 'orionwave[audio]'
```
- High-quality audio processing libraries
- Advanced pitch shifting

### Effects
```bash
pip install 'orionwave[effects]'
```
- Additional audio effects
- VST plugin support

### Machine Learning
```bash
pip install 'orionwave[ml]'
```
- Neural voice enhancement
- Auto-tune capabilities

### Development
```bash
pip install 'orionwave[dev]'
```
- Testing frameworks
- Code formatting tools
- Documentation generators

### Full Installation
```bash
pip install 'orionwave[all]'
```

## Platform-Specific Instructions

### Windows
1. Install Python 3.8+
2. Install Microsoft Visual C++ Build Tools
3. Install PortAudio:
   ```bash
   pip install pipwin
   pipwin install pyaudio
   ```

### Linux (Ubuntu/Debian)
```bash
# Install required system packages
sudo apt-get update
sudo apt-get install python3-dev portaudio19-dev

# Install OrionWave
pip install orionwave
```

### macOS
```bash
# Using Homebrew
brew install portaudio

# Install OrionWave
pip install orionwave
```

## Verifying Installation

```python
from orionwave import VoiceProcessor
from orionwave.config import AudioConfig

# Should run without errors
processor = VoiceProcessor(AudioConfig())
```

## Troubleshooting

### Common Issues

1. **PyAudio Installation Fails**
   - Windows: Use `pipwin install pyaudio`
   - Linux: Install `portaudio19-dev`
   - macOS: Install `portaudio` via Homebrew

2. **CUDA Not Found**
   - Only required for ML features
   - Install CUDA Toolkit from NVIDIA website

3. **GUI Import Errors**
   - Install GUI dependencies: `pip install 'orionwave[gui]'`

## Updating

To update to the latest version:
```bash
pip install --upgrade orionwave
```

## Uninstalling

```bash
pip uninstall orionwave
```