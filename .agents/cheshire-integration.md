# Cheshire BLE Light Integration

## Overview
Home Assistant custom integration for controlling Cheshire BLE LED lights (Keepsmile and compatible devices).

## Supported Devices
- KS03-* (old variant)
- KS03~* (new variant)

## Features
- RGB color control
- Brightness control (0-255)
- Effects: JUMP_7, JUMP_3, FADE_7, FADE_3, FLASH, AUTO
- Connect-send-disconnect pattern for reliable control
- Graceful disconnect handling

## Installation

### HACS Installation
1. Add this repository to HACS as a custom repository
2. Install the "Cheshire BLE Lights" integration
3. Restart Home Assistant
4. Go to Configuration → Integrations → Add Integration → Search for "Cheshire"
5. Select your device from the discovered list

### Manual Installation
1. Copy `custom_components/cheshire/` to your Home Assistant config directory
2. Restart Home Assistant
3. Add the integration via the UI

## Usage

### Light Entity
The integration creates a `light.cheshire_<address>` entity for each device.

**Services:**
- `light.turn_on` - Turn on with optional color, brightness, or effect
- `light.turn_off` - Turn off

**Example Automations:**

```yaml
# Turn on with red color
service: light.turn_on
target:
  entity_id: light.cheshire_23_01_01_b5_9c_be
data:
  rgb_color: [255, 0, 0]
  brightness: 255

# Turn on with effect
service: light.turn_on
target:
  entity_id: light.cheshire_23_01_01_b5_9c_be
data:
  effect: FLASH
  brightness: 200
```

## Testing

### Webcam Color Verification
Use the webcam tool to verify light colors:

```bash
# Check current color
agent_tools/.venv/bin/python agent_tools/webcam_avg_color.py 0

# Expected output format: R:<value> G:<value> B:<value>
```

### Direct Light Control Test
```bash
# Test light control
agent_tools/.venv/bin/python agent_tools/test_light.py

# Set specific color
agent_tools/.venv/bin/python agent_tools/set_green.py

# Turn off
agent_tools/.venv/bin/python agent_tools/turn_off.py
```

## Architecture

### Connection Pattern
The integration uses a connect-send-disconnect pattern:
1. Scan for device using HA's bluetooth manager
2. Connect to device
3. Send command(s)
4. Disconnect immediately

This ensures reliable operation even if the device goes to sleep or moves out of range.

### Key Files
- `__init__.py` - Entry setup, bluetooth callbacks
- `config_flow.py` - Device discovery and selection
- `light.py` - LightEntity implementation
- `coordinator.py` - DataUpdateCoordinator (minimal polling)
- `const.py` - Constants and effect mappings

### Dependencies
- `cheshire` library (~/projects/cheshire)
- Home Assistant bluetooth integration
- bleak (via HA's bluetooth manager)

## Troubleshooting

### Device Not Found
- Ensure device is powered on and in range
- Check that Bluetooth adapter is working
- Verify device name starts with KS03- or KS03~

### Connection Failures
- Move Bluetooth adapter closer to device
- Check for interference from other devices
- Restart Home Assistant

### Bluetooth Permissions Error
If you see "Missing NET_ADMIN/NET_RAW capabilities":
- This is an environment limitation, not an integration issue
- The integration will still work for discovered devices
- Full Bluetooth management requires elevated permissions

## Development

### Testing Changes
1. Edit files in `custom_components/cheshire/`
2. Copy to `~/.homeassistant/custom_components/cheshire/`
3. Restart Home Assistant
4. Check logs: `tail -f ~/.homeassistant/home-assistant.log | grep cheshire`

### Adding New Effects
Edit `const.py` to add effect names, then update `EFFECT_MAP` in `light.py`.

## License
MIT
