"""Select platform for SPRSUN Heat Pump Modbus."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CONF_SLAVE_ID,
    DEFAULT_SLAVE_ID,
    REG_WORK_MODE,
    REG_FAN_MODE,
    REG_PUMP_MODE,
    WORK_MODE_MAP,
    FAN_MODE_MAP,
    PUMP_MODE_MAP,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SPRSUN select entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][entry.entry_id]["client"]
    slave_id = entry.data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)

    selects = [
        SPRSUNSelect(
            coordinator,
            client,
            slave_id,
            "work_mode",
            "Work Mode",
            REG_WORK_MODE,
            "work_mode",
            WORK_MODE_MAP,
            True,  # Requires unit restart
        ),
        SPRSUNSelect(
            coordinator,
            client,
            slave_id,
            "fan_mode",
            "Fan Mode",
            REG_FAN_MODE,
            "fan_mode",
            FAN_MODE_MAP,
            False,
        ),
        SPRSUNSelect(
            coordinator,
            client,
            slave_id,
            "pump_mode",
            "Pump Mode",
            REG_PUMP_MODE,
            "pump_mode",
            PUMP_MODE_MAP,
            False,
        ),
    ]

    async_add_entities(selects)


class SPRSUNSelect(CoordinatorEntity, SelectEntity):
    """SPRSUN Heat Pump select entity."""

    def __init__(
        self,
        coordinator,
        client,
        slave_id,
        select_id,
        name,
        register,
        data_key,
        options_map,
        requires_restart=False,
    ):
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._client = client
        self._slave_id = slave_id
        self._select_id = select_id
        self._attr_name = f"SPRSUN {name}"
        self._attr_unique_id = f"{DOMAIN}_{select_id}"
        self._register = register
        self._data_key = data_key
        self._options_map = options_map
        self._requires_restart = requires_restart
        self._attr_options = list(options_map.values())
        # Select entity jsou v Controls sekci (bez entity_category)

    @property
    def current_option(self) -> str | None:
        """Return the current option."""
        value = self.coordinator.data.get(self._data_key)
        if value is not None and value in self._options_map:
            return self._options_map[value]
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        # Find the key for the selected option
        option_key = None
        for key, value in self._options_map.items():
            if value == option:
                option_key = key
                break

        if option_key is None:
            _LOGGER.error("Invalid option selected: %s", option)
            return

        # Log warning if this change requires unit restart
        if self._requires_restart:
            unit_on = self.coordinator.data.get("unit_on")
            if unit_on:
                _LOGGER.warning(
                    "Work mode change may require manual unit restart. "
                    "Unit On/OFF cannot be controlled via Modbus (read-only status)."
                )

        # Write the register
        success = await self.hass.async_add_executor_job(
            self._client.write_register,
            self._register,
            option_key,
            0,
            self._slave_id,
        )

        if success:
            await self.coordinator.async_request_refresh()
