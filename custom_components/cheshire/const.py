"""Constants for the Cheshire BLE Lights integration."""

from typing import Final

DOMAIN: Final = "cheshire"

DEVICE_TIMEOUT: Final = 30

# Device name prefixes to discover
LOCAL_NAMES: Final = {"KS03-", "KS03~"}

UPDATE_SECONDS: Final = 60

# Effects supported by KS03 devices
EFFECTS: Final[list[str]] = [
    "JUMP_7",
    "JUMP_3",
    "FADE_7",
    "FADE_3",
    "FLASH",
    "AUTO",
]
