# Webcam Color Averaging Tool

## Purpose
This tool captures frames from a webcam and calculates the average RGB color values across all pixels. Used to verify BLE light color changes by pointing the camera at the lights.

## Location
`agent_tools/webcam_avg_color.py`

## Usage

### Command Line
```bash
agent_tools/.venv/bin/python agent_tools/webcam_avg_color.py [camera]
```

**Parameters:**
- `camera` (optional): Camera index (integer) or device path (string)
  - Default: `0`
  - Examples: `0`, `1`, `/dev/video0`

**Output:**
```
R:<value> G:<value> B:<value>
```

### Python Import
```python
from agent_tools.webcam_avg_color import get_average_rgb

get_average_rgb(camera=0, num_frames=10)
```

**Parameters:**
- `camera` (int or str): Camera index or device path (default: 0)
- `num_frames` (int): Number of frames to average (default: 10)

## Examples

### Basic usage
```bash
agent_tools/.venv/bin/python agent_tools/webcam_avg_color.py
```

### Specify camera index
```bash
agent_tools/.venv/bin/python agent_tools/webcam_avg_color.py 1
```

### Use device path
```bash
agent_tools/.venv/bin/python agent_tools/webcam_avg_color.py /dev/video0
```

## Dependencies
Requires virtual environment with opencv-python and numpy:
```bash
uv venv agent_tools/.venv
uv pip install --python agent_tools/.venv/bin/python opencv-python numpy
```

## Notes
- Captures 10 frames by default and averages them for stability
- Skips first 5 frames to allow camera auto-exposure to settle
- Returns RGB values (0-255)
- If camera index fails, try different indices (0, 1, 2) or use device path
- PipeWire or other processes may lock camera devices
