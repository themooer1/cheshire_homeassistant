# Cheshire Home Assistant Integration

Control Keepsmile and compatible BLE LED strip lights directly from Home Assistant via Bluetooth.

## Installation

1. Install [HACS](https://hacs.xyz/docs/use/download/download/)
2. In HACS, add this repository as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories/) (category: Integration)
3. Search for "Cheshire BLE Lights" and install
4. Restart Home Assistant

## Usage

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for "Cheshire BLE Lights"
3. Select your device from the discovered list
4. Control your lights via the light entity created

## Supported Devices

See the [Cheshire project](https://github.com/themooer1/cheshire#supported-devices) for the full list of supported devices.

## Integration Tests

The `integration_tests/` folder contains end-to-end tests that control a physical BLE light through a real Home Assistant instance and verify the color change with a webcam.

### Quick start

```bash
bash integration_tests/run_integration_test.sh
```

This single command performs the full lifecycle: stops any running HA, resets the HA config, syncs the custom component, starts HA, completes onboarding (admin/admin123), adds the cheshire integration via the config flow, and runs the light control test with webcam verification. Exit code 0 means all tests passed.

### Prerequisites

- `~/projects/home-assistant-core` with a venv containing `hass` (HA core dev checkout)
- `~/projects/cheshire` installed and importable in HA's venv
- A Bluetooth adapter (e.g. `hci0`) that is UP
- A KS03 BLE light powered on and in range
- A webcam pointed at the light (`/dev/video0`)
- `sudo` access (HA runs as root for Bluetooth access)
- `agent_tools/.venv` with `websockets`, `opencv-python`, `numpy`, and `bleak`:
  ```bash
  uv venv agent_tools/.venv
  uv pip install --python agent_tools/.venv/bin/python websockets opencv-python numpy bleak
  ```

### What the test does

1. Turns the light on with RED, GREEN, and BLUE via the HA `light.turn_on` service
2. After each color, reads the webcam and checks the dominant RGB channel matches
3. Turns the light off and verifies the webcam goes dark
4. Reports pass/fail for each step

### Individual scripts

- **`run_integration_test.sh`** - Full orchestrator (run this)
- **`onboard_ha.py`** - Completes HA onboarding and creates a long-lived access token
- **`test_light_via_ha.py`** - Light control test with webcam verification (can be run standalone against an already-running HA)
- **`docker-compose.yml`** - Alternative containerized HA setup with Bluetooth passthrough

### Running the test against an already-running HA

If HA is already running with the integration loaded:

```bash
TOKEN=$(agent_tools/.venv/bin/python integration_tests/onboard_ha.py http://localhost:8123)
agent_tools/.venv/bin/python integration_tests/test_light_via_ha.py http://localhost:8123 "$TOKEN" light.ks03_b59cbe 0
```
