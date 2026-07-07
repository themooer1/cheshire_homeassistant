#!/usr/bin/env python3
"""Authenticate with HA and create a long-lived access token."""

import asyncio
import json
import websockets
import aiohttp

HA_URL = "http://localhost:8123"
HA_WS_URL = "ws://localhost:8123/api/websocket"
USERNAME = "admin"
PASSWORD = "admin123"

async def create_token():
    """Create a long-lived access token."""
    
    # First, authenticate via websocket to get a session
    async with websockets.connect(HA_WS_URL) as ws:
        # Wait for auth_required
        msg = await ws.recv()
        data = json.loads(msg)
        print(f"1. {data.get('type')}")
        
        if data.get('type') != 'auth_required':
            print("Unexpected message type")
            return None
        
        # Send auth message
        auth_msg = {
            "type": "auth",
            "access_token": ""  # We don't have a token yet
        }
        
        # Try to authenticate with username/password via the auth provider
        # This won't work directly, but let's see what happens
        await ws.send(json.dumps(auth_msg))
        
        msg = await ws.recv()
        data = json.loads(msg)
        print(f"2. {data.get('type')}: {data.get('message', '')}")
        
        if data.get('type') == 'auth_invalid':
            print("\nNeed to use OAuth2 flow")
            print("Creating token via REST API instead...")
            
            # Use the REST API to create a token
            async with aiohttp.ClientSession() as session:
                # First, get an auth code
                auth_url = f"{HA_URL}/auth/authorize?response_type=code&client_id=&redirect_uri="
                print(f"Auth URL: {auth_url}")
                
                # This won't work without a browser, so let's try a different approach
                print("\nAlternative: Use the HA UI to create a token")
                print("1. Open http://localhost:8123")
                print("2. Log in with admin/admin123")
                print("3. Go to Profile → Long-Lived Access Tokens → Create Token")
                
    return None

if __name__ == "__main__":
    asyncio.run(create_token())
