"""Binary sensor platform for SPRSUN Heat Pump Modbus."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SPRSUN binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    sensors = [
        # Component status sensors
        SPRSUNBinarySensor(coordinator, "pump", "Pump", "pump", BinarySensorDeviceClass.RUNNING),
        SPRSUNBinarySensor(coordinator, "comp_on", "Compressor", "comp_on", BinarySensorDeviceClass.RUNNING),
        SPRSUNBinarySensor(coordinator, "fan_on", "Fan", "fan_on", BinarySensorDeviceClass.RUNNING),
        SPRSUNBinarySensor(coordinator, "4way_valve", "4-Way Valve", "4way_valve", None),
        SPRSUNBinarySensor(coordinator, "three_valve", "3-Way Valve", "three_valve", None),
        SPRSUNBinarySensor(coordinator, "crank_heater", "Crank Heater", "crank_heater", BinarySensorDeviceClass.HEAT),
        SPRSUNBinarySensor(coordinator, "chassis_heater", "Chassis Heater", "chassis_heater", BinarySensorDeviceClass.HEAT),
        SPRSUNBinarySensor(coordinator, "heater", "Heater", "heater", BinarySensorDeviceClass.HEAT),

        # Switch/signal sensors
        SPRSUNBinarySensor(coordinator, "flow_switch", "Flow Switch", "flow_switch", BinarySensorDeviceClass.RUNNING),
        SPRSUNBinarySensor(coordinator, "ac_linkage", "A/C Linkage Switch", "ac_linkage", None),
        SPRSUNBinarySensor(coordinator, "sg_signal", "SG Signal", "sg_signal", None),
        SPRSUNBinarySensor(coordinator, "evu_signal", "EVU Signal", "evu_signal", None),

        # Linkage sensors
        SPRSUNBinarySensor(coordinator, "cooling_linkage", "Cooling Linkage", "cooling_linkage", BinarySensorDeviceClass.RUNNING),
        SPRSUNBinarySensor(coordinator, "heating_linkage", "Heating Linkage", "heating_linkage", BinarySensorDeviceClass.RUNNING),
        SPRSUNBinarySensor(coordinator, "terminal_pump", "Terminal Pump", "terminal_pump", BinarySensorDeviceClass.RUNNING),

        # Legacy sensors (kept for compatibility)
        SPRSUNBinarySensor(coordinator, "fan_high", "Fan High Speed", "fan_high", BinarySensorDeviceClass.RUNNING),
        SPRSUNBinarySensor(coordinator, "fan_low", "Fan Low Speed", "fan_low", BinarySensorDeviceClass.RUNNING),
    ]

    # Add alarm sensors - automatically from ALARM_REGISTERS in const.py
    from .const import ALARM_REGISTERS

    for alarm_id, alarm_name in ALARM_REGISTERS.items():
        sensors.append(
            SPRSUNBinarySensor(
                coordinator,
                f"alarm_{alarm_id}",
                alarm_name,  # Already includes "AL001", "AL002", etc.
                f"alarm_{alarm_id}",
                BinarySensorDeviceClass.PROBLEM,
                EntityCategory.DIAGNOSTIC,  # Alarmy jsou diagnostické
            )
        )

    async_add_entities(sensors)


class SPRSUNBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """SPRSUN Heat Pump binary sensor."""

    def __init__(self, coordinator, sensor_id, name, data_key, device_class, entity_category=None):
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._sensor_id = sensor_id
        self._attr_name = f"SPRSUN {name}"
        self._attr_unique_id = f"{DOMAIN}_{sensor_id}"
        self._data_key = data_key
        self._attr_device_class = device_class
        self._attr_entity_category = entity_category

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.coordinator.data.get(self._data_key)
