#!/usr/bin/env python3
"""Turn on lights with bright color for webcam verification."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "projects" / "cheshire"))

from bleak import BleakScanner
from cheshire.hal.devices import device_profile_from_ble_device
from cheshire.compiler.state import LightState
from cheshire.generic.command import SwitchCommand, BrightnessCommand, RGBCommand


async def main():
    print("Scanning for KS03 device...")
    devices = await BleakScanner.discover(timeout=5.0)
    
    device = None
    for d in devices:
        if d.name and (d.name.startswith("KS03-") or d.name.startswith("KS03~")):
            device = d
            break
    
    if not device:
        print("ERROR: No device found")
        return False
    
    print(f"Found: {device.name}")
    profile = device_profile_from_ble_device(device)
    connection = await profile.connect(device)
    
    # Turn on with bright green
    state = LightState()
    state.update(SwitchCommand(on=True))
    state.update(RGBCommand(red=0, green=255, blue=0))
    state.update(BrightnessCommand(brightness=255))
    
    print("Turning ON with GREEN color...")
    await connection.apply(state)
    await connection.disconnect()
    print("Done! Lights should be green now.")
    return True


if __name__ == "__main__":
    asyncio.run(main())
