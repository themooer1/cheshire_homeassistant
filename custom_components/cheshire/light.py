"""Cheshire BLE Lights light platform."""

from __future__ import annotations

import logging
from typing import Any

from bleak import BleakClient
from bleak.backends.device import BLEDevice
from bleak_retry_connector import establish_connection
from cheshire.compiler.state import LightState
from cheshire.generic.command import (
    BrightnessCommand,
    EffectCommand,
    RGBCommand,
    SwitchCommand,
)
from cheshire.generic.effect import Effect
from cheshire.hal.devices import Connection, device_profile_from_ble_device

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import CheshireConfigEntry
from .const import DOMAIN, EFFECTS

_LOGGER = logging.getLogger(__name__)

EFFECT_MAP = {
    "JUMP_7": Effect.JUMP_7,
    "JUMP_3": Effect.JUMP_3,
    "FADE_7": Effect.FADE_7,
    "FADE_3": Effect.FADE_3,
    "FLASH": Effect.FLASH,
    "AUTO": Effect.AUTO,
}

# Reverse map for tracking current effect
EFFECT_MAP_REVERSE = {v: k for k, v in EFFECT_MAP.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CheshireConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the light platform for Cheshire BLE."""
    data = hass.data[DOMAIN][entry.entry_id]
    ble_device: BLEDevice = data["ble_device"]
    address: str = data["address"]

    async_add_entities(
        [CheshireLight(hass, ble_device, address, entry.title, entry.entry_id)]
    )


class CheshireLight(LightEntity):
    """Representation of a Cheshire BLE light."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_should_poll = False
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_color_mode = ColorMode.RGB
    _attr_supported_features = LightEntityFeature.EFFECT
    _attr_effect_list = EFFECTS

    def __init__(
        self,
        hass: HomeAssistant,
        ble_device: BLEDevice,
        address: str,
        name: str,
        entry_id: str,
    ) -> None:
        """Initialize the light."""
        self._hass = hass
        self._entry_id = entry_id
        self._ble_device = ble_device
        self._address = address
        self._attr_unique_id = address
        self._attr_device_info = DeviceInfo(
            name=name,
            identifiers={(DOMAIN, address)},
            connections={("bluetooth", address)},
        )

        # Local state tracking
        self._attr_is_on = False
        self._attr_brightness = 255
        self._attr_rgb_color = (255, 255, 255)
        self._attr_effect = None

    def _get_ble_device(self) -> BLEDevice:
        """Get the latest BLE device reference from HA's bluetooth manager."""
        data = self._hass.data[DOMAIN].get(self._entry_id)
        if data and data.get("ble_device"):
            self._ble_device = data["ble_device"]
        return self._ble_device

    async def _send_state(self, state: LightState) -> None:
        """Connect to device via HA's bluetooth manager, send state, disconnect."""
        ble_device = self._get_ble_device()
        profile = device_profile_from_ble_device(ble_device)
        if profile is None:
            _LOGGER.error(
                "Could not find device profile for %s", self._address
            )
            return

        connection: Connection | None = None
        client: BleakClient | None = None
        try:
            client = await establish_connection(
                BleakClient,
                ble_device,
                name=self._attr_device_info.get("name", self._address),
            )
            transmitter = profile.get_transmitter(client)
            connection = Connection(profile.compiler(), transmitter)
            await connection.apply(state)
        except Exception as ex:
            _LOGGER.error(
                "Failed to send command to %s: %s", self._address, ex
            )
        finally:
            if connection:
                try:
                    await connection.disconnect()
                except Exception:
                    _LOGGER.debug(
                        "Error disconnecting from %s (may already be disconnected)",
                        self._address,
                    )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        state = LightState()
        state.update(SwitchCommand(on=True))

        brightness = kwargs.get(ATTR_BRIGHTNESS, self.brightness or 255)
        rgb = kwargs.get(ATTR_RGB_COLOR, self.rgb_color or (255, 255, 255))

        if ATTR_EFFECT in kwargs:
            effect_name = kwargs[ATTR_EFFECT]
            effect = EFFECT_MAP.get(effect_name)
            if effect:
                state.update(EffectCommand(effect=effect))
                state.update(BrightnessCommand(brightness=brightness))
                self._attr_effect = effect_name
                await self._send_state(state)
                self._attr_is_on = True
                self.async_write_ha_state()
                return

        if ATTR_RGB_COLOR in kwargs:
            rgb = kwargs[ATTR_RGB_COLOR]

        if ATTR_BRIGHTNESS in kwargs or ATTR_RGB_COLOR in kwargs:
            state.update(RGBCommand(red=rgb[0], green=rgb[1], blue=rgb[2]))
            state.update(BrightnessCommand(brightness=brightness))

        self._attr_rgb_color = rgb
        self._attr_brightness = brightness
        self._attr_effect = None

        await self._send_state(state)
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        state = LightState()
        state.update(SwitchCommand(on=False))
        await self._send_state(state)
        self._attr_is_on = False
        self.async_write_ha_state()
