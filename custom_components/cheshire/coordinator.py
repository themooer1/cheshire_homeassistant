"""The Cheshire BLE Lights coordinator."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, UPDATE_SECONDS

_LOGGER = logging.getLogger(__name__)


class CheshireCoordinator(DataUpdateCoordinator[None]):
    """Coordinator for Cheshire BLE Lights.

    Since Cheshire devices don't support reading state (connect-send-disconnect pattern),
    this coordinator only serves as a periodic refresh trigger. State is tracked locally.
    """

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"Cheshire {entry.title}",
            update_interval=timedelta(seconds=UPDATE_SECONDS),
        )

    async def _async_update_data(self) -> None:
        """No-op update since we can't read device state."""
        return None
