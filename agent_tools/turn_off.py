#!/usr/bin/env python3
"""Turn off lights."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "projects" / "cheshire"))

from bleak import BleakScanner
from cheshire.hal.devices import device_profile_from_ble_device
from cheshire.compiler.state import LightState
from cheshire.generic.command import SwitchCommand


async def main():
    devices = await BleakScanner.discover(timeout=5.0)
    device = None
    for d in devices:
        if d.name and (d.name.startswith("KS03-") or d.name.startswith("KS03~")):
            device = d
            break
    
    if not device:
        print("ERROR: No device found")
        return
    
    profile = device_profile_from_ble_device(device)
    connection = await profile.connect(device)
    state = LightState()
    state.update(SwitchCommand(on=False))
    await connection.apply(state)
    await connection.disconnect()
    print("Lights turned off")


if __name__ == "__main__":
    asyncio.run(main())
