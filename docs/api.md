# API Reference

## Overview

This document provides a comprehensive reference for OrionWave's audio processing system.

## Core Modules

- [`orionwave.processor`](#processor-module): Core audio processing
- [`orionwave.effects`](#effects-module): Audio effects implementation
- [`orionwave.audio`](#audio-module): Audio analysis and enhancement
- [`orionwave.gui`](#gui-module): Graphical interface components

---

## Processor Module

### `VoiceProcessor` Class

The main class for audio processing and effect management.

```python
processor = VoiceProcessor(config: AudioConfig)
```

#### Methods

- `initialize_streams(input_device_index: Optional[int] = None, output_device_index: Optional[int] = None)`
  - Initializes audio input/output streams
  - Parameters:
    - `input_device_index`: Index of input device
    - `output_device_index`: Index of output device

- `add_effect(effect_name: str, params: Dict = None)`
  - Adds an effect to the processing chain
  - Parameters:
    - `effect_name`: Name of the effect
    - `params`: Effect parameters

- `process_audio(effect: str = 'pitch_shift', **kwargs)`
  - Processes audio with the specified effect
  - Parameters:
    - `effect`: Effect name
    - `**kwargs`: Effect-specific parameters

#### Examples

```python
from orionwave import VoiceProcessor, AudioConfig

# Initialize
config = AudioConfig()
processor = VoiceProcessor(config)

# Add effects
processor.add_effect('pitch_shift', {'shift': 200})
processor.add_effect('reverb', {'room_size': 0.8})

# Start processing
processor.initialize_streams()
```

## Effects Module

Available audio effects and their parameters.

### Basic Effects

- `pitch_shift`
  - `shift`: Pitch shift amount (-1200 to 1200 cents)
- `robot_effect`
  - `frequency`: Modulation frequency (Hz)
- `reverb`
  - `room_size`: Size of virtual room (0.0 to 1.0)
  - `damping`: High-frequency damping (0.0 to 1.0)

### Advanced Effects

- `noise_reduction`
  - `strength`: Reduction strength (0.0 to 1.0)
- `auto_tune`
  - `scale`: Musical scale for correction
- `compressor`
  - `threshold`: Compression threshold (-60 to 0 dB)
  - `ratio`: Compression ratio (1.0 to 20.0)

## Audio Module

### `AudioAnalyzer` Class

Real-time audio analysis capabilities.

```python
analyzer = AudioAnalyzer(sample_rate: int, chunk_size: int)
```

#### Methods

- `analyze_frame(frame: np.ndarray) -> Dict[str, float]`
  - Analyzes audio frame
  - Returns metrics including:
    - RMS level
    - Dominant frequency
    - Spectral centroid
    - Signal clarity

### `AudioEnhancer` Class

Neural audio enhancement features.

```python
enhancer = AudioEnhancer(model_path: Optional[str] = None)
```

## GUI Module

### `VoiceChangerGUI` Class

Qt-based graphical interface.

```python
app = VoiceChangerGUI()
```

#### Features

- Real-time visualization
- Effect parameter controls
- Device selection
- Preset management
- Performance monitoring

## Network Module

### `VoiceChangerServer` Class

WebSocket server for remote control.

```python
server = VoiceChangerServer(processor, host='localhost', port=8765)
```

#### Methods

- `start()`: Starts WebSocket server
- `process_command(command: str, params: Dict)`: Processes remote commands

## Examples

See the [Examples and Tutorials](./examples.md) for practical usage examples.