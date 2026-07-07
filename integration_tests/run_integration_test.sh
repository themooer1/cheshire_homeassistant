#!/usr/bin/env bash
#
# Integration test for the Cheshire Home Assistant integration.
#
# This script controls a REAL Home Assistant instance (running locally from
# ~/projects/home-assistant-core with a venv) and verifies that the cheshire
# custom integration can control a physical BLE light, confirmed via webcam.
#
# It performs the full lifecycle:
#   1. Stop any running HA
#   2. Reset the HA config dir to a clean slate
#   3. Sync the custom component from the repo
#   4. Start HA as root (for bluetooth access)
#   5. Complete onboarding (admin/admin123) via REST API
#   6. Create a long-lived access token
#   7. Add the cheshire integration via the HA config flow
#   8. Run the light control test with webcam verification
#
# Prerequisites:
#   - podman/docker NOT required (uses local HA core checkout)
#   - ~/projects/home-assistant-core with venv (bin/hass)
#   - ~/projects/cheshire installed and importable in HA's venv
#   - A bluetooth adapter (hci0) that is UP
#   - A KS03 BLE light in range and powered on
#   - A webcam pointed at the light (/dev/video0)
#   - sudo access (for bluetooth + HA runs as root)
#   - agent_tools/.venv with websockets, opencv-python, numpy, bleak
#
set -euo pipefail

REPO="/home/user/projects/cheshire-homeassistant"
HA_CORE="/home/user/projects/home-assistant-core"
HA_VENV="$HA_CORE/venv"
HA_CONFIG="/home/user/.homeassistant"
HA_URL="http://localhost:8123"
HA_LOG="/tmp/ha_integration.log"
TOKEN_FILE="/tmp/ha_integration_token"
CLIENT_ID="$HA_URL/"
ENTITY_ID="${HA_ENTITY_ID:-light.ks03_b59cbe}"
CAMERA="${WEBCAM:-0}"

cd "$REPO"

echo "=== Stopping any running HA ==="
sudo pkill -f "venv/bin/hass" 2>/dev/null || true
sleep 2

echo "=== Resetting HA config dir ==="
sudo rm -rf "$HA_CONFIG"
mkdir -p "$HA_CONFIG/custom_components"
echo "default_config:" > "$HA_CONFIG/configuration.yaml"

echo "=== Syncing cheshire custom component ==="
cp -r "$REPO/custom_components/cheshire" "$HA_CONFIG/custom_components/cheshire"
rm -rf "$HA_CONFIG/custom_components/cheshire/__pycache__"

echo "=== Starting HA as root ==="
sudo bash -c "$HA_VENV/bin/hass --config $HA_CONFIG > $HA_LOG 2>&1 &"

echo "=== Waiting for HA to boot ==="
for i in $(seq 1 90); do
    if sudo ss -tlnp 2>/dev/null | grep -q 8123; then
        echo "HA is listening on port 8123 (after ${i}x2s)"
        break
    fi
    sleep 2
done

echo "=== Completing onboarding ==="
"$REPO/agent_tools/.venv/bin/python" "$REPO/integration_tests/onboard_ha.py" "$HA_URL" > "$TOKEN_FILE"
TOKEN=$(cat "$TOKEN_FILE")
echo "Long-lived token created and saved to $TOKEN_FILE"

echo "=== Adding cheshire integration via config flow ==="
# Initiate the config flow
FLOW=$(curl -s -X POST "$HA_URL/api/config/config_entries/flow" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"handler":"cheshire"}')
FLOW_ID=$(echo "$FLOW" | python3 -c "import sys,json; print(json.load(sys.stdin).get('flow_id',''))")

if [ -z "$FLOW_ID" ]; then
    echo "ERROR: Config flow did not start. Response:"
    echo "$FLOW"
    exit 1
fi

echo "Flow started: $FLOW_ID"

# Find the KS03 device address from the flow's schema options
DEVICE_ADDR=$(echo "$FLOW" | python3 -c "
import sys, json
flow = json.load(sys.stdin)
for field in flow.get('data_schema', []):
    if field.get('name') == 'address':
        opts = field.get('options', [])
        if opts:
            print(opts[0][0])
            break
")

if [ -z "$DEVICE_ADDR" ]; then
    echo "ERROR: No KS03 device discovered by HA bluetooth. Make sure the light is on and in range."
    exit 1
fi

echo "Discovered device: $DEVICE_ADDR"

# Complete the config flow
RESULT=$(curl -s -X POST "$HA_URL/api/config/config_entries/flow/$FLOW_ID" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"address\":\"$DEVICE_ADDR\"}")
echo "Config flow result: $(echo $RESULT | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("type"), d.get("title",""))')"

# Wait for the integration to set up
echo "Waiting for integration to load..."
sleep 8

# Derive the entity_id by querying HA for light entities containing "ks03"
ENTITY_ID=$(curl -s "$HA_URL/api/states" -H "Authorization: Bearer $TOKEN" | \
    python3 -c "
import sys, json
states = json.load(sys.stdin)
match = next((s['entity_id'] for s in states if s['entity_id'].startswith('light.') and 'ks03' in s['entity_id'].lower()), None)
print(match or 'light.ks03_b59cbe')
")
echo "Entity ID: $ENTITY_ID"

echo "=== Running light control test with webcam verification ==="
"$REPO/agent_tools/.venv/bin/python" "$REPO/integration_tests/test_light_via_ha.py" "$HA_URL" "$TOKEN" "$ENTITY_ID" "$CAMERA"
TEST_EXIT=$?

echo "=== Test complete (exit code: $TEST_EXIT) ==="
echo "HA log: $HA_LOG"

exit $TEST_EXIT
