"""Climate platform for SPRSUN Heat Pump Modbus."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CONF_SLAVE_ID,
    DEFAULT_SLAVE_ID,
    REG_WORK_MODE,
    REG_HEATING_SETPOINT,
    REG_COOLING_SETPOINT,
    REG_HOTWATER_SETPOINT,
    DISCRETE_UNIT_ON,
    WORK_MODE_COOLING,
    WORK_MODE_HEATING,
    WORK_MODE_HOT_WATER,
    WORK_MODE_HW_COOLING,
    WORK_MODE_HW_HEATING,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SPRSUN climate entity."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][entry.entry_id]["client"]
    slave_id = entry.data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)

    async_add_entities([SPRSUNClimate(coordinator, client, slave_id)])


class SPRSUNClimate(CoordinatorEntity, ClimateEntity):
    """SPRSUN Heat Pump Climate entity."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_hvac_modes = [
        HVACMode.OFF,
        HVACMode.HEAT,
        HVACMode.COOL,
        HVACMode.HEAT_COOL,
    ]
    _attr_min_temp = 10
    _attr_max_temp = 70
    _attr_target_temperature_step = 0.5

    def __init__(self, coordinator, client, slave_id):
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._client = client
        self._slave_id = slave_id
        self._attr_name = "SPRSUN Heat Pump"
        self._attr_unique_id = f"{DOMAIN}_climate"

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self.coordinator.data.get("outlet_temp")

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        work_mode = self.coordinator.data.get("work_mode")
        
        if work_mode in [WORK_MODE_HEATING, WORK_MODE_HW_HEATING]:
            return self.coordinator.data.get("heating_setpoint")
        elif work_mode in [WORK_MODE_COOLING, WORK_MODE_HW_COOLING]:
            return self.coordinator.data.get("cooling_setpoint")
        elif work_mode == WORK_MODE_HOT_WATER:
            return self.coordinator.data.get("hotwater_setpoint")
        
        return self.coordinator.data.get("heating_setpoint")

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        unit_on = self.coordinator.data.get("unit_on")
        
        if not unit_on:
            return HVACMode.OFF
        
        work_mode = self.coordinator.data.get("work_mode")
        
        if work_mode == WORK_MODE_HEATING or work_mode == WORK_MODE_HW_HEATING:
            return HVACMode.HEAT
        elif work_mode == WORK_MODE_COOLING or work_mode == WORK_MODE_HW_COOLING:
            return HVACMode.COOL
        elif work_mode == WORK_MODE_HOT_WATER:
            return HVACMode.HEAT_COOL
        
        return HVACMode.OFF

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        work_mode = self.coordinator.data.get("work_mode")

        _LOGGER.info("Setting temperature to %.1f°C (current work_mode: %s)", temperature, work_mode)

        success = False
        if work_mode in [WORK_MODE_HEATING, WORK_MODE_HW_HEATING]:
            _LOGGER.info("Writing heating setpoint to register 1 (40002)")
            success = await self.hass.async_add_executor_job(
                self._client.write_register,
                REG_HEATING_SETPOINT,
                temperature,
                1,
                self._slave_id,
            )
        elif work_mode in [WORK_MODE_COOLING, WORK_MODE_HW_COOLING]:
            _LOGGER.info("Writing cooling setpoint to register 2 (40003)")
            success = await self.hass.async_add_executor_job(
                self._client.write_register,
                REG_COOLING_SETPOINT,
                temperature,
                1,
                self._slave_id,
            )
        elif work_mode == WORK_MODE_HOT_WATER:
            _LOGGER.info("Writing hot water setpoint to register 3 (40004)")
            success = await self.hass.async_add_executor_job(
                self._client.write_register,
                REG_HOTWATER_SETPOINT,
                temperature,
                1,
                self._slave_id,
            )

        if success:
            _LOGGER.info("Temperature setpoint written successfully")
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to write temperature setpoint")

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""
        _LOGGER.info("Setting HVAC mode to: %s", hvac_mode)

        if hvac_mode == HVACMode.OFF:
            # NOTE: According to manufacturer's table, there is no coil for turning unit OFF
            # Unit On/OFF (10001) is read-only status
            # We log warning and skip - user may need to turn off unit manually
            _LOGGER.warning("Cannot turn off unit via Modbus - Unit On/OFF is read-only. Please turn off manually or check device documentation.")
        else:
            # Set the work mode directly - this should activate the unit
            new_work_mode = None
            if hvac_mode == HVACMode.HEAT:
                new_work_mode = WORK_MODE_HEATING
                _LOGGER.info("Setting work mode to HEATING (1)")
            elif hvac_mode == HVACMode.COOL:
                new_work_mode = WORK_MODE_COOLING
                _LOGGER.info("Setting work mode to COOLING (0)")
            elif hvac_mode == HVACMode.HEAT_COOL:
                new_work_mode = WORK_MODE_HOT_WATER
                _LOGGER.info("Setting work mode to HOT_WATER (2)")

            if new_work_mode is not None:
                # Set work mode - this should start the unit in the selected mode
                _LOGGER.info("Writing work mode %d to register 0 (40001)", new_work_mode)
                success = await self.hass.async_add_executor_job(
                    self._client.write_register,
                    REG_WORK_MODE,
                    new_work_mode,
                    0,  # INT type, no decimal places
                    self._slave_id,
                )

                if success:
                    _LOGGER.info("Work mode set successfully to %d", new_work_mode)
                else:
                    _LOGGER.error("Failed to set work mode to %d", new_work_mode)

        await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        """Turn on the unit."""
        # According to manufacturer's table, unit is controlled via Mode setP register
        # Set to last known mode or default to HEATING
        current_mode = self.coordinator.data.get("work_mode", WORK_MODE_HEATING)
        _LOGGER.info("Turning on unit by setting work mode to %d", current_mode)

        success = await self.hass.async_add_executor_job(
            self._client.write_register,
            REG_WORK_MODE,
            current_mode,
            0,
            self._slave_id,
        )
        if success:
            _LOGGER.info("Unit turned on successfully")
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to turn on unit")

    async def async_turn_off(self) -> None:
        """Turn off the unit."""
        # NOTE: According to manufacturer's table, there is no coil for turning unit OFF
        # Unit On/OFF (10001) is read-only status
        _LOGGER.warning("Cannot turn off unit via Modbus - Unit On/OFF is read-only. Please turn off manually or check device documentation.")
        await self.coordinator.async_request_refresh()
