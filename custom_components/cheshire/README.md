# Cheshire BLE Lights - Home Assistant Integration

A HACS-compatible integration for controlling Cheshire-compatible BLE lights (KS03 variants) via Home Assistant.

## Supported Devices

- KS03- (older variant)
- KS03~ (new variant, e.g., KS03~B59CBE)

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL
6. Select "Integration" as the category
7. Click "Add"
8. Install the integration
9. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/cheshire/` directory to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services
2. Click "Add Integration"
3. Search for "Cheshire BLE Lights"
4. Select your device from the discovered Bluetooth devices
5. The light entity will be created automatically

## Features

- **RGB Color Control**: Set any color via the color picker
- **Brightness Control**: Adjust brightness from 0-255
- **Effects**: Built-in effects including:
  - JUMP_7: 7-color jump effect
  - JUMP_3: 3-color jump effect
  - FADE_7: 7-color fade effect
  - FADE_3: 3-color fade effect
  - FLASH: Flash effect
  - AUTO: Automatic cycling

## Architecture

The integration uses a **connect-send-disconnect** pattern:
- Each command establishes a BLE connection
- Sends the compiled light state
- Immediately disconnects
- This ensures reliable operation and avoids connection timeouts

State is tracked locally since the devices don't support reading current state.

## Requirements

- Home Assistant 2024.1.0 or later
- Bluetooth adapter with passive scanning support
- `cheshire` Python library (installed automatically via requirements)

## Troubleshooting

### Device Not Found
- Ensure your device is powered on
- Check that Bluetooth is enabled in Home Assistant
- Verify the device name starts with "KS03-" or "KS03~"

### Connection Failures
- Move the Bluetooth adapter closer to the device
- Check for Bluetooth interference
- Restart the integration

## Development

```bash
# Clone the repository
git clone <this-repo>

# Install in development mode
cd home-assistant-core
pip install -e ../cheshire
pip install -e ../cheshire-homeassistant
```
