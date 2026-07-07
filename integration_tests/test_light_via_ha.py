#!/usr/bin/env python3
"""Test the Cheshire BLE light integration through Home Assistant.

Controls the light via the HA REST API (light.turn_on / light.turn_off) and
verifies the physical light color using the webcam. This tests the full path:
HA -> cheshire integration -> BLE -> physical light -> webcam.

Prerequisites:
- HA running with the cheshire integration loaded and a light entity configured
- A long-lived access token (run onboard_ha.py to get one)

Usage:
    python3 test_light_via_ha.py [HA_URL] [TOKEN] [ENTITY_ID] [CAMERA]

Exit code 0 = all tests passed, 1 = some test failed.
"""

import sys
import time
import urllib.request
import urllib.error
import json
import subprocess
import os

HA_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8123"
TOKEN = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("HA_TOKEN", "")
ENTITY_ID = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("HA_ENTITY_ID", "light.ks03_b59cbe")
CAMERA = sys.argv[4] if len(sys.argv) > 4 else os.environ.get("WEBCAM", "0")

WEBCAM_SCRIPT = os.path.join(os.path.dirname(__file__), "..", "agent_tools", "webcam_avg_color.py")
VENV_PYTHON = os.path.join(os.path.dirname(__file__), "..", "agent_tools", ".venv", "bin", "python")

SETTLE_TIME = 4.0
DOMINANCE_MARGIN = 30
OFF_BRIGHTNESS_THRESHOLD = 60
MIN_BRIGHTNESS = 40
RETRY_READS = 2
HTTP_RETRIES = 3
HTTP_RETRY_DELAY = 5


def _headers():
    return {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


def _post(path, payload):
    data = json.dumps(payload).encode()
    last_err = None
    for attempt in range(HTTP_RETRIES):
        req = urllib.request.Request(HA_URL + path, data=data, headers=_headers(), method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.status, resp.read().decode()
        except (urllib.error.HTTPError,) as e:
            return e.code, e.read().decode()
        except Exception as e:
            last_err = e
            time.sleep(HTTP_RETRY_DELAY)
    raise last_err


def _get(path):
    req = urllib.request.Request(HA_URL + path, headers=_headers())
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, {}


def get_entity():
    status, data = _get(f"/api/states/{ENTITY_ID}")
    return data if status == 200 else None


def call_service(domain, service, payload):
    status, body = _post(f"/api/services/{domain}/{service}", payload)
    return status == 200


def turn_on(rgb=None, brightness=255, effect=None):
    payload = {"entity_id": ENTITY_ID}
    if rgb is not None:
        payload["rgb_color"] = list(rgb)
    if brightness is not None:
        payload["brightness"] = brightness
    if effect is not None:
        payload["effect"] = effect
    return call_service("light", "turn_on", payload)


def turn_off():
    return call_service("light", "turn_off", {"entity_id": ENTITY_ID})


def read_webcam_color():
    cmd = [VENV_PYTHON, WEBCAM_SCRIPT, str(CAMERA)]
    for attempt in range(RETRY_READS + 1):
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            continue
        out = result.stdout.strip()
        parts = {}
        for token in out.replace(",", " ").split():
            if ":" in token:
                k, v = token.split(":", 1)
                parts[k.upper()] = int(v)
        if "R" in parts and "G" in parts and "B" in parts:
            rgb = (parts["R"], parts["G"], parts["B"])
            if max(rgb) >= MIN_BRIGHTNESS or attempt == RETRY_READS:
                return rgb
            time.sleep(1)
    return None


def assert_color(name, expected_rgb, actual_rgb):
    er, eg, eb = expected_rgb
    ar, ag, ab = actual_rgb
    expected_dominant = expected_rgb.index(max(expected_rgb))
    actual_dominant = actual_rgb.index(max(actual_rgb))
    if actual_dominant != expected_dominant:
        print(f"  [FAIL] {name}: expected {['R','G','B'][expected_dominant]} dominant, "
              f"got {['R','G','B'][actual_dominant]} dominant (R{ar} G{ag} B{ab})", file=sys.stderr)
        return False
    expected_max = max(expected_rgb)
    actual_max = max(actual_rgb)
    if actual_max < DOMINANCE_MARGIN:
        print(f"  [FAIL] {name}: webcam too dark (R{ar} G{ag} B{ab}, max {actual_max})", file=sys.stderr)
        return False
    others = [v for i, v in enumerate(actual_rgb) if i != expected_dominant]
    if max(others) > actual_max - DOMINANCE_MARGIN:
        print(f"  [FAIL] {name}: dominant channel not clear enough "
              f"(R{ar} G{ag} B{ab}, max {actual_max}, second {max(others)})", file=sys.stderr)
        return False
    print(f"  [PASS] {name}: {['R','G','B'][expected_dominant]} dominant (R{ar} G{ag} B{ab})")
    return True


def assert_off(name, actual_rgb):
    ar, ag, ab = actual_rgb
    brightness = (ar + ag + ab) / 3
    if brightness < OFF_BRIGHTNESS_THRESHOLD:
        print(f"  [PASS] {name}: webcam dark (R{ar} G{ag} B{ab}, avg {brightness:.0f})")
        return True
    print(f"  [FAIL] {name}: webcam still bright (R{ar} G{ag} B{ab}, avg {brightness:.0f})", file=sys.stderr)
    return False


def run_test():
    results = []

    print("=" * 60, file=sys.stderr)
    print("Cheshire HA Integration Test", file=sys.stderr)
    print(f"HA: {HA_URL}  Entity: {ENTITY_ID}  Camera: {CAMERA}", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    if not TOKEN:
        print("[FAIL] No token provided (arg 2 or HA_TOKEN env)", file=sys.stderr)
        return False

    print("\n1. Checking API connectivity...", file=sys.stderr)
    status, _ = _get("/api/")
    if status != 200:
        print(f"  [FAIL] API not reachable (status {status})", file=sys.stderr)
        return False
    print("  [PASS] API reachable")

    print("\n2. Checking entity exists...", file=sys.stderr)
    entity = get_entity()
    if not entity:
        print(f"  [FAIL] Entity {ENTITY_ID} not found", file=sys.stderr)
        return False
    print(f"  [PASS] Entity found: state={entity['state']}")
    print(f"         supported_color_modes={entity['attributes'].get('supported_color_modes')}")
    print(f"         effect_list={entity['attributes'].get('effect_list')}")

    print("\n3. Turning ON with RED (255,0,0)...", file=sys.stderr)
    if not turn_on(rgb=(255, 0, 0), brightness=255):
        print("  [FAIL] turn_on service call failed", file=sys.stderr)
        return False
    time.sleep(SETTLE_TIME)
    entity = get_entity()
    print(f"  State: {entity['state']}, rgb: {entity['attributes'].get('rgb_color')}", file=sys.stderr)
    color = read_webcam_color()
    if not color:
        print("  [FAIL] Could not read webcam color", file=sys.stderr)
        return False
    results.append(assert_color("RED", (255, 0, 0), color))

    print("\n4. Turning ON with GREEN (0,255,0)...", file=sys.stderr)
    if not turn_on(rgb=(0, 255, 0), brightness=255):
        print("  [FAIL] turn_on service call failed", file=sys.stderr)
        return False
    time.sleep(SETTLE_TIME)
    entity = get_entity()
    print(f"  State: {entity['state']}, rgb: {entity['attributes'].get('rgb_color')}", file=sys.stderr)
    color = read_webcam_color()
    if not color:
        print("  [FAIL] Could not read webcam color", file=sys.stderr)
        return False
    results.append(assert_color("GREEN", (0, 255, 0), color))

    print("\n5. Turning ON with BLUE (0,0,255)...", file=sys.stderr)
    if not turn_on(rgb=(0, 0, 255), brightness=255):
        print("  [FAIL] turn_on service call failed", file=sys.stderr)
        return False
    time.sleep(SETTLE_TIME)
    entity = get_entity()
    print(f"  State: {entity['state']}, rgb: {entity['attributes'].get('rgb_color')}", file=sys.stderr)
    color = read_webcam_color()
    if not color:
        print("  [FAIL] Could not read webcam color", file=sys.stderr)
        return False
    results.append(assert_color("BLUE", (0, 0, 255), color))

    print("\n6. Turning OFF...", file=sys.stderr)
    if not turn_off():
        print("  [FAIL] turn_off service call failed", file=sys.stderr)
        return False
    time.sleep(SETTLE_TIME)
    entity = get_entity()
    print(f"  State: {entity['state']}", file=sys.stderr)
    color = read_webcam_color()
    if color:
        results.append(assert_off("OFF", color))
    else:
        print("  [SKIP] Could not read webcam for OFF test", file=sys.stderr)

    print("\n" + "=" * 60, file=sys.stderr)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} passed", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    return passed == total and total > 0


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
