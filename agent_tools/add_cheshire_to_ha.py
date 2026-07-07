#!/usr/bin/env python3
"""Add cheshire integration to HA config entries."""

import json
import time
from datetime import datetime, timezone
from pathlib import Path

CONFIG_FILE = Path.home() / ".homeassistant/.storage/core.config_entries"
DEVICE_ADDRESS = "23:01:01:B5:9C:BE"

# Load current config
with open(CONFIG_FILE) as f:
    config = json.load(f)

# Check if cheshire already exists
for entry in config["data"]["entries"]:
    if entry["domain"] == "cheshire":
        print(f"Cheshire integration already exists: {entry['entry_id']}")
        exit(0)

# Create new entry
now = datetime.now(timezone.utc).isoformat()
new_entry = {
    "created_at": now,
    "data": {
        "address": DEVICE_ADDRESS
    },
    "disabled_by": None,
    "discovery_keys": {},
    "domain": "cheshire",
    "entry_id": f"cheshire_{int(time.time())}",
    "minor_version": 1,
    "modified_at": now,
    "options": {},
    "pref_disable_new_entities": False,
    "pref_disable_polling": False,
    "source": "user",
    "subentries": [],
    "title": "Cheshire BLE Light",
    "unique_id": DEVICE_ADDRESS,
    "version": 1
}

config["data"]["entries"].append(new_entry)

# Save
with open(CONFIG_FILE, "w") as f:
    json.dump(config, f, indent=2)

print(f"Added cheshire integration: {new_entry['entry_id']}")
print("Restart Home Assistant to load the integration")
