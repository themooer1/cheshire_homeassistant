#!/usr/bin/env python3
"""Test cheshire integration via HA websocket API."""

import asyncio
import json
import sys
import websockets

HA_WS_URL = "ws://localhost:8123/api/websocket"
ENTITY_ID = "light.cheshire_ble_light"

async def test_integration():
    """Test the cheshire integration via websocket."""
    
    try:
        async with websockets.connect(HA_WS_URL) as ws:
            # Wait for auth_required
            msg = await ws.recv()
            data = json.loads(msg)
            print(f"1. Received: {data.get('type')}")
            
            if data.get('type') == 'auth_required':
                # Try to authenticate with internal API
                # This won't work without a token, but let's see what happens
                print("Authentication required")
                print("\nTo test the integration, you need to:")
                print("1. Open http://localhost:8123 in a browser")
                print("2. Log in (create an account if needed)")
                print("3. Go to Profile (click user icon bottom-left)")
                print("4. Scroll to 'Long-Lived Access Tokens'")
                print("5. Click 'Create Token' and copy it")
                print("\nThen use the token with the HA REST API:")
                print(f"curl -X POST -H 'Authorization: Bearer YOUR_TOKEN' \\")
                print(f"  -H 'Content-Type: application/json' \\")
                print(f"  -d '{{\"entity_id\": \"{ENTITY_ID}\"}}' \\")
                print(f"  http://localhost:8123/api/services/light/turn_on")
                return False
            
    except Exception as e:
        print(f"Connection failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(test_integration())
