"""Switch platform for SPRSUN Heat Pump Modbus."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CONF_SLAVE_ID,
    DEFAULT_SLAVE_ID,
    COIL_UNIT_ON,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SPRSUN switches."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][entry.entry_id]["client"]
    slave_id = entry.data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)

    switches = [
        SPRSUNSwitch(coordinator, client, slave_id, "unit_on", "Unit Power", COIL_UNIT_ON, "unit_on"),
    ]

    async_add_entities(switches)


class SPRSUNSwitch(CoordinatorEntity, SwitchEntity):
    """SPRSUN Heat Pump switch entity."""

    def __init__(self, coordinator, client, slave_id, switch_id, name, coil, data_key):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._client = client
        self._slave_id = slave_id
        self._switch_id = switch_id
        self._attr_name = f"SPRSUN {name}"
        self._attr_unique_id = f"{DOMAIN}_{switch_id}"
        self._coil = coil
        self._data_key = data_key

    @property
    def is_on(self) -> bool | None:
        """Return true if switch is on."""
        return self.coordinator.data.get(self._data_key)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        success = await self.hass.async_add_executor_job(
            self._client.write_coil,
            self._coil,
            True,
            self._slave_id,
        )
        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        success = await self.hass.async_add_executor_job(
            self._client.write_coil,
            self._coil,
            False,
            self._slave_id,
        )
        if success:
            await self.coordinator.async_request_refresh()
