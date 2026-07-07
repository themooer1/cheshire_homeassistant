#!/usr/bin/env python3
import asyncio
import sys

from bleak import BleakScanner


async def scan_for_ks03(timeout: float = 10.0) -> str | None:
    devices = await BleakScanner.discover(timeout=timeout)

    ks03_devices = [
        d for d in devices
        if d.name and d.name.startswith("KS03")
    ]

    if not ks03_devices:
        return None

    device = ks03_devices[0]
    suffix = device.name[-6:]
    print(f"Found: {device.name} ({device.address})")
    print(f"Suffix: {suffix}")
    return suffix


def main():
    timeout = 10.0
    if len(sys.argv) > 1:
        try:
            timeout = float(sys.argv[1])
        except ValueError:
            print(f"Error: Invalid timeout value: {sys.argv[1]}", file=sys.stderr)
            sys.exit(1)

    try:
        result = asyncio.run(scan_for_ks03(timeout))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if result is None:
        print("Error: No KS03 device found", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
