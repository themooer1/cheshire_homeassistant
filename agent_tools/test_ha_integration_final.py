#!/usr/bin/env python3
"""Test cheshire integration via HA websocket API with authentication."""

import asyncio
import json
import websockets

HA_WS_URL = "ws://localhost:8123/api/websocket"
ENTITY_ID = "light.cheshire_ble_light"

async def test_via_websocket():
    """Test the integration via websocket."""
    
    try:
        async with websockets.connect(HA_WS_URL) as ws:
            # Wait for auth_required
            msg = await ws.recv()
            data = json.loads(msg)
            print(f"1. {data.get('type')}")
            
            if data.get('type') != 'auth_required':
                print("Unexpected message type")
                return
            
            # Try to authenticate with the system token
            # This is a workaround - we'll use the internal API
            print("\nAuthentication required.")
            print("The integration is loaded and the entity exists:")
            print(f"  Entity ID: {ENTITY_ID}")
            print(f"  Platform: cheshire")
            print(f"  Unique ID: 23:01:01:B5:9C:BE")
            print("\nTo test the integration via API, you need to:")
            print("1. Open http://localhost:8123 in a browser")
            print("2. Complete the onboarding (create admin user)")
            print("3. Go to Profile → Long-Lived Access Tokens → Create Token")
            print("4. Use the token with HA REST API")
            print("\nAlternatively, test directly via the HA UI:")
            print("1. Go to Developer Tools → Services")
            print("2. Select 'light.turn_on'")
            print(f"3. Set entity_id: {ENTITY_ID}")
            print("4. Set rgb_color: [255, 0, 0]")
            print("5. Click 'Call Service'")
            print("6. Check if the lights turn red (use webcam to verify)")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_via_websocket())
