# BLE Device Scanner (KS03)

## Purpose
Scans for Bluetooth LE devices and finds KS03 lights (names starting with "KS03" or "KS03~"). Reports the last 6 characters of the device name, which is the unique device identifier used for connections.

## Location
`agent_tools/ble_scan.py`

## Usage

### Command Line
```bash
agent_tools/.venv/bin/python agent_tools/ble_scan.py [timeout]
```

**Parameters:**
- `timeout` (optional): Scan duration in seconds (float)
  - Default: `10.0`
  - Recommended: `5.0` to `15.0`

**Output:**
```
Found: KS03-ABCD (XX:XX:XX:XX:XX:XX)
Suffix: -ABCD
```

**Exit codes:**
- `0`: KS03 device found, suffix printed
- `1`: Error (no adapter, no devices found, invalid arguments)

### Python Import
```python
from agent_tools.ble_scan import scan_for_ks03

suffix = await scan_for_ks03(timeout=10.0)
```

**Returns:** `str | None` — last 6 characters of the device name, or `None` if no KS03 found.

## Examples

### Default 10-second scan
```bash
agent_tools/.venv/bin/python agent_tools/ble_scan.py
```

### Quick 5-second scan
```bash
agent_tools/.venv/bin/python agent_tools/ble_scan.py 5
```

## Dependencies
Requires virtual environment with bleak:
```bash
uv venv agent_tools/.venv
uv pip install --python agent_tools/.venv/bin/python bleak
```

## Notes
- Requires a Bluetooth adapter (USB or built-in) that is UP and RUNNING
- On Linux, uses D-Bus (BlueZ) backend via bleak
- The KS03 device name format is `KS03-XXXX` (old) or `KS03~XXXX` (new), where XXXX is the unique suffix
- If multiple KS03 devices are found, the first one discovered is reported
- Scan time of 5-10 seconds is usually sufficient; increase if devices are not found
