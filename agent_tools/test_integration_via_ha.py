#!/usr/bin/env python3
"""
Test script for Cheshire Home Assistant integration.

This script verifies that the integration is working correctly.

Prerequisites:
1. Home Assistant running with cheshire integration loaded
2. Long-lived access token created via HA UI

Usage:
1. Create a long-lived access token:
   - Open http://localhost:8123
   - Log in with admin/admin123
   - Go to Profile (bottom-left) → Long-Lived Access Tokens → Create Token
   - Copy the token

2. Run this script:
   python test_integration_via_ha.py YOUR_TOKEN
"""

import sys
import time
import requests
from pathlib import Path

# Add cheshire to path
sys.path.insert(0, str(Path.home() / "projects" / "cheshire"))

HA_URL = "http://localhost:8123"
ENTITY_ID = "light.cheshire_ble_light"

def test_integration(token):
    """Test the cheshire integration via HA API."""
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("Testing Cheshire Home Assistant Integration")
    print("=" * 60)
    
    # Test 1: Check API connection
    print("\n1. Testing API connection...")
    try:
        response = requests.get(f"{HA_URL}/api/", headers=headers, timeout=5)
        if response.status_code == 200:
            print("   ✓ API connection successful")
        else:
            print(f"   ✗ API connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ API connection failed: {e}")
        return False
    
    # Test 2: Check entity exists
    print("\n2. Checking entity exists...")
    response = requests.get(f"{HA_URL}/api/states/{ENTITY_ID}", headers=headers, timeout=5)
    if response.status_code == 200:
        entity = response.json()
        print(f"   ✓ Entity found: {entity['entity_id']}")
        print(f"   State: {entity['state']}")
        print(f"   Attributes: {entity.get('attributes', {})}")
    else:
        print(f"   ✗ Entity not found: {response.status_code}")
        return False
    
    # Test 3: Turn on with red color
    print("\n3. Turning on with RED color...")
    response = requests.post(
        f"{HA_URL}/api/services/light/turn_on",
        headers=headers,
        json={
            "entity_id": ENTITY_ID,
            "rgb_color": [255, 0, 0],
            "brightness": 255
        },
        timeout=10
    )
    if response.status_code == 200:
        print("   ✓ Service call successful")
        print("   Waiting 3 seconds for light to change...")
        time.sleep(3)
        
        # Check state
        response = requests.get(f"{HA_URL}/api/states/{ENTITY_ID}", headers=headers, timeout=5)
        if response.status_code == 200:
            entity = response.json()
            print(f"   State: {entity['state']}")
            print(f"   RGB: {entity.get('attributes', {}).get('rgb_color')}")
    else:
        print(f"   ✗ Service call failed: {response.status_code}")
        return False
    
    # Test 4: Turn off
    print("\n4. Turning off...")
    response = requests.post(
        f"{HA_URL}/api/services/light/turn_off",
        headers=headers,
        json={"entity_id": ENTITY_ID},
        timeout=10
    )
    if response.status_code == 200:
        print("   ✓ Service call successful")
        print("   Waiting 2 seconds for light to turn off...")
        time.sleep(2)
        
        # Check state
        response = requests.get(f"{HA_URL}/api/states/{ENTITY_ID}", headers=headers, timeout=5)
        if response.status_code == 200:
            entity = response.json()
            print(f"   State: {entity['state']}")
    else:
        print(f"   ✗ Service call failed: {response.status_code}")
        return False
    
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("\nTo verify with webcam, run:")
    print("  agent_tools/.venv/bin/python agent_tools/webcam_avg_color.py 0")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_integration_via_ha.py YOUR_TOKEN")
        print("\nTo create a token:")
        print("1. Open http://localhost:8123")
        print("2. Log in with admin/admin123")
        print("3. Go to Profile → Long-Lived Access Tokens → Create Token")
        sys.exit(1)
    
    token = sys.argv[1]
    success = test_integration(token)
    sys.exit(0 if success else 1)
