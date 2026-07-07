#!/usr/bin/env python3
"""Set up and test cheshire integration via HA websocket API."""

import asyncio
import json
import sys
import websockets
from pathlib import Path

HA_URL = "ws://localhost:8123/api/websocket"
DEVICE_NAME = "KS03~B59CBE"
DEVICE_ADDRESS = "23:01:01:B5:9C:BE"

async def setup_and_test():
    """Set up cheshire integration and test it."""
    
    # Connect to HA websocket
    try:
        async with websockets.connect(HA_URL) as ws:
            # Wait for auth_required
            msg = await ws.recv()
            data = json.loads(msg)
            print(f"Received: {data.get('type')}")
            
            if data.get('type') == 'auth_required':
                # We need to authenticate
                # For now, we'll try to use the internal API
                print("Authentication required - need to create a long-lived access token")
                print("Please create a token via the HA web interface:")
                print("1. Go to http://localhost:8123")
                print("2. Click on your user profile (bottom left)")
                print("3. Scroll to 'Long-Lived Access Tokens'")
                print("4. Click 'Create Token'")
                print("5. Copy the token and use it with the HA API")
                return False
            
    except Exception as e:
        print(f"Connection failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(setup_and_test())
