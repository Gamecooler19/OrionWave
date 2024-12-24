# OrionWave - Professional Real-Time Voice Changer

**OrionWave** is a professional-grade voice changing system designed for real-time audio processing. It offers multiple effects, advanced audio processing capabilities, and a customizable framework for voice manipulation.

---

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Basic Usage](#basic-usage)
- [Installation Options](#installation-options)
- [Documentation](#documentation)
- [Examples](#examples)
  - [Basic Voice Effects](#basic-voice-effects)
  - [Advanced Configuration](#advanced-configuration)
  - [Custom Effects](#custom-effects)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- 🎙️ **Real-time Processing**: Low-latency voice manipulation
- 🎛️ **Multiple Effects**: Pitch shifting, robot voice, reverb, and more
- 📊 **Audio Analysis**: Real-time spectrum analysis and visualization
- 🔧 **Extensible System**: Plugin support for custom effects
- ⚡ **Performance Optimized**: Efficient audio processing pipeline

## Getting Started

### Prerequisites

- Python 3.8+
- PortAudio (for PyAudio)
- ALSA development files (Linux)

### Installation

```bash
# Install basic package
pip install orionwave

# For development
pip install -e .
```

### Basic Usage

```python
from orionwave import VoiceProcessor, AudioConfig

# Initialize with default settings
processor = VoiceProcessor(AudioConfig())

# Add effects
processor.add_effect('pitch_shift', {'shift': 100})
processor.add_effect('reverb', {'mix': 0.5})

# Start processing
processor.initialize_streams()
```

---

## Installation Options

```bash
# Full installation
pip install orionwave[all]

# Core features only
pip install orionwave

# With VST support
pip install orionwave[vst]
```

## Documentation

For detailed documentation, refer to:
- [User Guide](./docs/user_guide.md)
- [API Reference](./docs/api.md)
- [Effect Documentation](./docs/effects.md)
- [Configuration Guide](./docs/config.md)

## Examples

### Basic Voice Effects

```python
from orionwave import VoiceProcessor, AudioConfig

processor = VoiceProcessor(AudioConfig())

# Simple pitch shift
processor.add_effect('pitch_shift', {'shift': 200})

# Robot voice effect
processor.add_effect('robot', {})
```

### Advanced Configuration

```python
config = AudioConfig()
config.RATE = 48000
config.CHUNK = 1024
config.FORMAT = 16

processor = VoiceProcessor(config)
```

### Custom Effects

```python
def custom_effect(data, config):
    """Example custom effect implementation"""
    # Process audio data
    processed = data * 1.5  # Simple amplification
    return processed

processor.effects_registry['custom'] = custom_effect
processor.add_effect('custom', {})
```

## Configuration

OrionWave uses a YAML configuration file for customizing behavior:

```yaml
audio:
  rate: 48000
  chunk: 1024
  channels: 1
  format: 16

effects:
  pitch_shift:
    enabled: true
    default_shift: 100
  
  reverb:
    enabled: true
    room_size: 0.8
    damping: 0.5
    
  equalizer:
    enabled: true
    bands:
      - {freq: 100, gain: 0.0, q: 0.7}
      - {freq: 1000, gain: 0.0, q: 0.7}
      - {freq: 10000, gain: 0.0, q: 0.7}
```

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone repository
git clone https://github.com/Gamecooler19/orionwave.git
cd orionwave

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install development dependencies
pip install -e ".[dev]"
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- PortAudio team for audio I/O support
- NumPy community for numerical processing capabilities
- PyQt team for the GUI framework
- All contributors and users of OrionWave

---

For more information, bug reports, or feature requests, please visit our [GitHub repository](https://github.com/Gamecooler19/orionwave).