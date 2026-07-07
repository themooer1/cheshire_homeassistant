#!/usr/bin/env python3
"""Test script to verify cheshire light control works."""

import asyncio
import sys
from pathlib import Path

# Add cheshire to path
sys.path.insert(0, str(Path.home() / "projects" / "cheshire"))

from bleak import BleakScanner
from cheshire.hal.devices import device_profile_from_ble_device
from cheshire.compiler.state import LightState
from cheshire.generic.command import SwitchCommand, BrightnessCommand, RGBCommand, EffectCommand
from cheshire.generic.effect import Effect


async def find_device():
    """Scan for KS03 device."""
    print("Scanning for KS03 devices...")
    devices = await BleakScanner.discover(timeout=5.0)
    
    for device in devices:
        if device.name and (device.name.startswith("KS03-") or device.name.startswith("KS03~")):
            print(f"Found: {device.name} ({device.address})")
            return device
    
    print("No KS03 device found")
    return None


async def test_light_control(device):
    """Test turning light on with red color."""
    print(f"\nConnecting to {device.name}...")
    
    profile = device_profile_from_ble_device(device)
    if not profile:
        print("ERROR: Could not get device profile")
        return False
    
    try:
        connection = await profile.connect(device)
        print("Connected!")
        
        # Turn on with red color
        state = LightState()
        state.update(SwitchCommand(on=True))
        state.update(RGBCommand(red=255, green=0, blue=0))
        state.update(BrightnessCommand(brightness=255))
        
        print("Sending: Turn ON, Red color, Full brightness")
        await connection.apply(state)
        print("Command sent successfully!")
        
        await connection.disconnect()
        print("Disconnected")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_turn_off(device):
    """Test turning light off."""
    print(f"\nConnecting to {device.name}...")
    
    profile = device_profile_from_ble_device(device)
    if not profile:
        print("ERROR: Could not get device profile")
        return False
    
    try:
        connection = await profile.connect(device)
        print("Connected!")
        
        state = LightState()
        state.update(SwitchCommand(on=False))
        
        print("Sending: Turn OFF")
        await connection.apply(state)
        print("Command sent successfully!")
        
        await connection.disconnect()
        print("Disconnected")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False


async def main():
    """Main test routine."""
    print("=" * 60)
    print("Cheshire Light Control Test")
    print("=" * 60)
    
    # Find device
    device = await find_device()
    if not device:
        print("\nTest FAILED: No device found")
        return False
    
    # Test turning on with red
    print("\n" + "=" * 60)
    print("TEST 1: Turn ON with RED color")
    print("=" * 60)
    success1 = await test_light_control(device)
    
    if success1:
        print("\nWaiting 3 seconds for light to change...")
        await asyncio.sleep(3)
        
        # Test turning off
        print("\n" + "=" * 60)
        print("TEST 2: Turn OFF")
        print("=" * 60)
        success2 = await test_turn_off(device)
    else:
        success2 = False
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    print(f"Turn ON with RED: {'PASS' if success1 else 'FAIL'}")
    print(f"Turn OFF: {'PASS' if success2 else 'FAIL'}")
    
    if success1 and success2:
        print("\nAll tests PASSED!")
        return True
    else:
        print("\nSome tests FAILED")
        return False


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
