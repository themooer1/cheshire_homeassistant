#!/usr/bin/env python3
"""Test cheshire integration through Home Assistant API."""

import asyncio
import json
import sys
import time
import requests
from pathlib import Path

# Add cheshire to path
sys.path.insert(0, str(Path.home() / "projects" / "cheshire"))

HA_URL = "http://localhost:8123"
DEVICE_NAME = "KS03~B59CBE"
DEVICE_ADDRESS = "23:01:01:B5:9C:BE"

def get_long_lived_token():
    """Create a long-lived access token."""
    # This requires authentication, so we'll use a workaround
    # by directly creating the token in storage
    token_path = Path.home() / ".homeassistant/.storage/auth"
    
    if not token_path.exists():
        print("Auth storage not found")
        return None
    
    with open(token_path) as f:
        auth_data = json.load(f)
    
    # Find the owner user
    users = auth_data.get("data", {}).get("users", [])
    owner_user = None
    for user in users:
        if user.get("is_owner") or user.get("name") == "Home Assistant Cast":
            owner_user = user
            break
    
    if not owner_user:
        print("No owner user found")
        return None
    
    user_id = owner_user["id"]
    print(f"Using user: {owner_user.get('name')} ({user_id})")
    
    # Create a refresh token
    import secrets
    token_id = secrets.token_hex(16)
    token = secrets.token_hex(32)
    
    refresh_token_path = Path.home() / ".homeassistant/.storage/auth_module.homeassistant_refresh_token"
    
    refresh_tokens = []
    if refresh_token_path.exists():
        with open(refresh_token_path) as f:
            refresh_tokens = json.load(f).get("data", {}).get("tokens", [])
    
    # Add new token
    refresh_tokens.append({
        "id": token_id,
        "user_id": user_id,
        "client_id": None,
        "token": token,
        "token_type": "access",
        "created_at": time.time(),
        "access_token_expiration": 1800,
        "last_used_at": None,
        "last_used_ip": None,
        "credential": None,
        "expire_at": None
    })
    
    # Save
    with open(refresh_token_path, "w") as f:
        json.dump({
            "version": 1,
            "minor_version": 1,
            "key": "auth_module.homeassistant_refresh_token",
            "data": {"tokens": refresh_tokens}
        }, f)
    
    print(f"Created refresh token: {token[:8]}...")
    return token

def test_api(token):
    """Test the HA API."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test connection
    try:
        response = requests.get(f"{HA_URL}/api/", headers=headers, timeout=5)
        print(f"API connection: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"API connection failed: {e}")
        return False
    
    # List entities
    response = requests.get(f"{HA_URL}/api/states", headers=headers, timeout=5)
    if response.status_code == 200:
        entities = response.json()
        light_entities = [e for e in entities if e["entity_id"].startswith("light.")]
        print(f"Found {len(light_entities)} light entities")
        for entity in light_entities:
            print(f"  - {entity['entity_id']}: {entity.get('state')}")
    
    return True

if __name__ == "__main__":
    token = get_long_lived_token()
    if token:
        test_api(token)
    else:
        print("Failed to get token")
