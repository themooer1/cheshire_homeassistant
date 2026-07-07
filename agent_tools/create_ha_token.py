#!/usr/bin/env python3
"""Create a long-lived access token for HA API testing."""

import json
import secrets
import time
from pathlib import Path

AUTH_FILE = Path.home() / ".homeassistant/.storage/auth"

# Read auth file with sudo
import subprocess
result = subprocess.run(["sudo", "cat", str(AUTH_FILE)], capture_output=True, text=True)
auth_data = json.loads(result.stdout)

# Find admin user
admin_user = None
for user in auth_data["data"]["users"]:
    if "system-admin" in user.get("group_ids", []):
        admin_user = user
        break

if not admin_user:
    print("No admin user found")
    exit(1)

print(f"Using user: {admin_user['name']} ({admin_user['id']})")

# Create new refresh token
token_id = secrets.token_hex(16)
access_token = secrets.token_hex(32)

new_token = {
    "id": token_id,
    "user_id": admin_user["id"],
    "client_id": None,
    "client_name": "Integration Test",
    "client_icon": None,
    "token_type": "system",
    "created_at": time.time(),
    "access_token": access_token,
    "expire_at": None,
    "last_used_at": None,
    "last_used_ip": None
}

auth_data["data"]["refresh_tokens"].append(new_token)

# Save with sudo
with open("/tmp/auth_new.json", "w") as f:
    json.dump(auth_data, f, indent=2)

subprocess.run(["sudo", "cp", "/tmp/auth_new.json", str(AUTH_FILE)])
subprocess.run(["sudo", "chown", "root:root", str(AUTH_FILE)])
subprocess.run(["sudo", "chmod", "600", str(AUTH_FILE)])

print(f"\nCreated long-lived access token:")
print(f"{access_token}")
print(f"\nUse this token with the HA API:")
print(f"curl -H 'Authorization: Bearer {access_token}' \\")
print(f"  http://localhost:8123/api/states")
