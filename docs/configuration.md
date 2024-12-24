# Configuration Guide

## Configuration Methods

OrionWave can be configured using:
1. YAML configuration files
2. Environment variables
3. Direct parameter setting

## Using Configuration Files

Create a `config.yaml`:

```yaml
# Audio settings
CHUNK: 1024
FORMAT: 16
CHANNELS: 1
RATE: 44100

# Effects settings
EFFECTS:
  pitch_shift:
    default_shift: 200
  reverb:
    room_size: 0.8
    damping: 0.5
  noise_reduction:
    enabled: true
    strength: 0.7

# Device settings
DEVICES:
  input: "default"
  output: "default"

# Neural enhancement
ML:
  model_path: "models/enhancer.pth"
  use_gpu: true
```

Loading configuration:
```python
from orionwave.config import AudioConfig

config = AudioConfig.from_yaml('config.yaml')
processor = VoiceProcessor(config)
```

## Environment Variables

```bash
export ORIONWAVE_CHUNK_SIZE=1024
export ORIONWAVE_SAMPLE_RATE=44100
export ORIONWAVE_CHANNELS=1
export ORIONWAVE_EFFECTS_ENABLED="pitch_shift,reverb"
```

## Parameters Reference

### Audio Settings

- `CHUNK`: Buffer size (default: 1024)
- `FORMAT`: Audio format (16/24/32 bit)
- `CHANNELS`: Number of channels (1=mono, 2=stereo)
- `RATE`: Sample rate (Hz)

### Effect Settings

- `pitch_shift`:
  - `default_shift`: Base pitch shift amount
  - `range`: Allowed shift range
- `reverb`:
  - `room_size`: Virtual room size
  - `damping`: High frequency damping
- `noise_reduction`:
  - `enabled`: Enable/disable
  - `strength`: Reduction strength

### Device Settings

- `input_device`: Input device name/index
- `output_device`: Output device name/index
- `buffer_size`: Device buffer size

### Performance Settings

- `latency_target`: Target latency (ms)
- `processing_threads`: Number of processing threads
- `use_gpu`: Enable GPU acceleration

## Best Practices

1. **Latency Optimization**
   ```yaml
   CHUNK: 512  # Smaller chunks = lower latency
   buffer_size: 1024  # Adjust based on system
   ```

2. **Quality vs Performance**
   ```yaml
   FORMAT: 24  # Higher bit depth
   RATE: 48000  # Higher sample rate
   processing_threads: 4  # More threads
   ```

3. **Resource Management**
   ```yaml
   use_gpu: false  # CPU-only mode
   effects_enabled: ["pitch_shift"]  # Limit active effects
   ```

## Example Configurations

### Low Latency Setup
```yaml
CHUNK: 256
FORMAT: 16
RATE: 44100
buffer_size: 512
latency_target: 10
```

### High Quality Setup
```yaml
CHUNK: 1024
FORMAT: 24
RATE: 48000
effects:
  all_enabled: true
  quality: "high"
```

### Performance Mode
```yaml
CHUNK: 2048
FORMAT: 16
RATE: 44100
effects:
  minimal_processing: true
use_gpu: false
```