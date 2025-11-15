"""Sensor platform for SPRSUN Heat Pump Modbus."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfPressure,
    UnitOfPower,
    UnitOfElectricPotential,
    UnitOfElectricCurrent,
    UnitOfTime,
    UnitOfVolumeFlowRate,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, STATUS_MAP, COMP_STATUS_MAP, UNIT_RUN_MODE_MAP, HEATER_TYPE_MAP, SG_MODE_MAP, WEEKDAY_MAP


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SPRSUN sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    sensors = [
        # Temperature sensors
        SPRSUNTemperatureSensor(coordinator, "inlet_temp", "Inlet Temperature", "inlet_temp"),
        SPRSUNTemperatureSensor(coordinator, "outlet_temp", "Outlet Temperature", "outlet_temp"),
        SPRSUNTemperatureSensor(coordinator, "ambient_temp", "Ambient Temperature", "ambient_temp"),
        SPRSUNTemperatureSensor(coordinator, "hotwater_temp", "Hot Water Temperature", "hotwater_temp"),
        SPRSUNTemperatureSensor(coordinator, "discharge_temp", "Discharge Temperature", "discharge_temp"),
        SPRSUNTemperatureSensor(coordinator, "suction_temp", "Suction Temperature", "suction_temp"),
        SPRSUNTemperatureSensor(coordinator, "coil_temp", "Coil Temperature", "coil_temp"),
        SPRSUNTemperatureSensor(coordinator, "suction_sh", "Suction Superheat", "suction_sh"),
        
        # Pressure sensors
        SPRSUNPressureSensor(coordinator, "discharge_press", "Discharge Pressure", "discharge_press"),
        SPRSUNPressureSensor(coordinator, "suction_press", "Suction Pressure", "suction_press"),
        
        # Percentage sensors
        SPRSUNPercentageSensor(coordinator, "fan_output", "Fan Output", "fan_output"),
        SPRSUNPercentageSensor(coordinator, "pump_output", "Pump Output", "pump_output"),
        SPRSUNPercentageSensor(coordinator, "dc_fan1_output", "DC Fan 1 Output", "dc_fan1_output"),
        SPRSUNPercentageSensor(coordinator, "dc_fan2_output", "DC Fan 2 Output", "dc_fan2_output"),
        SPRSUNPercentageSensor(coordinator, "required_cap", "Required Capacity", "required_cap"),
        SPRSUNPercentageSensor(coordinator, "actual_cap", "Actual Capacity", "actual_cap"),
        
        # Speed and feedback sensors
        SPRSUNSensor(coordinator, "actual_speed", "Actual Speed", "actual_speed", "RPM"),
        SPRSUNSensor(coordinator, "dc_fan1_feedback", "DC Fan 1 Feedback", "dc_fan1_feedback", "RPM"),
        SPRSUNSensor(coordinator, "dc_fan2_feedback", "DC Fan 2 Feedback", "dc_fan2_feedback", "RPM"),
        SPRSUNSensor(coordinator, "eev_opening", "EEV Opening", "eev_opening", None),
        SPRSUNSensor(coordinator, "comp_protection", "Compressor Protection", "comp_protection", None),
        
        # Status sensors
        SPRSUNStatusSensor(coordinator, "status", "Status", "status"),
        SPRSUNCompressorStatusSensor(coordinator, "comp_status", "Compressor Status", "comp_status"),
        SPRSUNUnitRunModeSensor(coordinator, "unit_run_mode", "Unit Run Mode", "unit_run_mode"),
        SPRSUNHeaterTypeSensor(coordinator, "heater_type", "Heater Type", "heater_type"),

        # Power sensors
        SPRSUNPowerSensor(coordinator, "bldc_power", "BLDC Power", "bldc_power"),
        SPRSUNVoltageSensor(coordinator, "bldc_var", "BLDC Var", "bldc_var"),
        SPRSUNCurrentSensor(coordinator, "bldc_current", "BLDC Current", "bldc_current"),
        SPRSUNPowerSensor(coordinator, "unit_power", "Unit Power", "unit_power"),

        # COP sensor
        SPRSUNSensor(coordinator, "unit_cop", "Unit COP", "unit_cop", None),

        # Water flow sensor
        SPRSUNFlowSensor(coordinator, "water_flow", "Water Flow", "water_flow"),

        # Working hours sensors
        SPRSUNTimeSensor(coordinator, "working_hours_pump", "Pump Working Hours", "working_hours_pump"),
        SPRSUNTimeSensor(coordinator, "working_hours_comp", "Compressor Working Hours", "working_hours_comp"),
        SPRSUNTimeSensor(coordinator, "working_hours_fan", "Fan Working Hours", "working_hours_fan"),
        SPRSUNTimeSensor(coordinator, "working_hours_3way", "3-Way Valve Working Hours", "working_hours_3way"),

        # Version and unit type sensors
        SPRSUNVersionSensor(coordinator, "version", "Firmware Version"),
        SPRSUNUnitTypeSensor(coordinator, "unit_type", "Unit Type"),
        SPRSUNSensor(coordinator, "comp_delay", "Compressor Delay", "comp_delay", "s"),
        SPRSUNTemperatureSensor(coordinator, "ext_temp_setp", "External Temperature Setpoint", "ext_temp_setp"),

        # Time setting sensors
        SPRSUNSensor(coordinator, "year", "Year", "year", None),
        SPRSUNSensor(coordinator, "month", "Month", "month", None),
        SPRSUNSensor(coordinator, "day", "Day", "day", None),
        SPRSUNSensor(coordinator, "hour", "Hour", "hour", None),
        SPRSUNSensor(coordinator, "minute", "Minute", "minute", None),
        SPRSUNWeekdaySensor(coordinator, "week", "Weekday", "week"),

        # Electric Meter sensors
        SPRSUNVoltageSensor(coordinator, "phase_voltage_a", "Phase Voltage A", "phase_voltage_a"),
        SPRSUNVoltageSensor(coordinator, "phase_voltage_b", "Phase Voltage B", "phase_voltage_b"),
        SPRSUNVoltageSensor(coordinator, "phase_voltage_c", "Phase Voltage C", "phase_voltage_c"),
        SPRSUNCurrentSensor(coordinator, "phase_current_a", "Phase Current A", "phase_current_a"),
        SPRSUNCurrentSensor(coordinator, "phase_current_b", "Phase Current B", "phase_current_b"),
        SPRSUNCurrentSensor(coordinator, "phase_current_c", "Phase Current C", "phase_current_c"),
        SPRSUNPowerSensor(coordinator, "power_w", "Power", "power_w"),
        SPRSUNEnergySensor(coordinator, "total_power_consumption", "Total Power Consumption", "total_power_consumption"),
        SPRSUNEnergySensor(coordinator, "record_power_1", "Power Consumption Record 1", "record_power_1"),
        SPRSUNEnergySensor(coordinator, "record_power_2", "Power Consumption Record 2", "record_power_2"),
        SPRSUNEnergySensor(coordinator, "record_power_3", "Power Consumption Record 3", "record_power_3"),
        SPRSUNEnergySensor(coordinator, "record_power_4", "Power Consumption Record 4", "record_power_4"),
        SPRSUNEnergySensor(coordinator, "record_power_5", "Power Consumption Record 5", "record_power_5"),
        SPRSUNEnergySensor(coordinator, "record_power_6", "Power Consumption Record 6", "record_power_6"),
        SPRSUNEnergySensor(coordinator, "record_power_7", "Power Consumption Record 7", "record_power_7"),

        # SG Ready sensors
        SPRSUNSGModeSensor(coordinator, "sg_mode", "SG Mode", "sg_mode"),
        SPRSUNSensor(coordinator, "sg_mode_change_holdtime", "SG Mode Change Hold Time", "sg_mode_change_holdtime", "s"),
        SPRSUNTemperatureSensor(coordinator, "sg_mode_w_tank_setp", "SG Mode Water Tank Setpoint", "sg_mode_w_tank_setp"),

        # Anti-legionella sensors
        SPRSUNTemperatureSensor(coordinator, "antileg_temp_setp", "Anti-Legionella Temperature Setpoint", "antileg_temp_setp"),
        SPRSUNWeekdaySensor(coordinator, "antileg_weekday", "Anti-Legionella Weekday", "antileg_weekday"),
        SPRSUNSensor(coordinator, "antileg_time_start", "Anti-Legionella Start Time", "antileg_time_start", None),
        SPRSUNSensor(coordinator, "antileg_time_end", "Anti-Legionella End Time", "antileg_time_end", None),
    ]

    async_add_entities(sensors)


class SPRSUNSensor(CoordinatorEntity, SensorEntity):
    """Base sensor for SPRSUN Heat Pump."""

    def __init__(self, coordinator, sensor_id, name, data_key, unit):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_id = sensor_id
        self._attr_name = f"SPRSUN {name}"
        self._attr_unique_id = f"{DOMAIN}_{sensor_id}"
        self._data_key = data_key
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._data_key)


class SPRSUNTemperatureSensor(SPRSUNSensor):
    """Temperature sensor."""

    def __init__(self, coordinator, sensor_id, name, data_key):
        """Initialize the temperature sensor."""
        super().__init__(coordinator, sensor_id, name, data_key, UnitOfTemperature.CELSIUS)
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT


class SPRSUNPressureSensor(SPRSUNSensor):
    """Pressure sensor."""

    def __init__(self, coordinator, sensor_id, name, data_key):
        """Initialize the pressure sensor."""
        super().__init__(coordinator, sensor_id, name, data_key, UnitOfPressure.BAR)
        self._attr_device_class = SensorDeviceClass.PRESSURE
        self._attr_state_class = SensorStateClass.MEASUREMENT


class SPRSUNPercentageSensor(SPRSUNSensor):
    """Percentage sensor."""

    def __init__(self, coordinator, sensor_id, name, data_key):
        """Initialize the percentage sensor."""
        super().__init__(coordinator, sensor_id, name, data_key, PERCENTAGE)
        self._attr_state_class = SensorStateClass.MEASUREMENT


class SPRSUNPowerSensor(SPRSUNSensor):
    """Power sensor."""

    def __init__(self, coordinator, sensor_id, name, data_key):
        """Initialize the power sensor."""
        super().__init__(coordinator, sensor_id, name, data_key, UnitOfPower.WATT)
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT


class SPRSUNVoltageSensor(SPRSUNSensor):
    """Voltage sensor."""

    def __init__(self, coordinator, sensor_id, name, data_key):
        """Initialize the voltage sensor."""
        super().__init__(coordinator, sensor_id, name, data_key, UnitOfElectricPotential.VOLT)
        self._attr_device_class = SensorDeviceClass.VOLTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT


class SPRSUNCurrentSensor(SPRSUNSensor):
    """Current sensor."""

    def __init__(self, coordinator, sensor_id, name, data_key):
        """Initialize the current sensor."""
        super().__init__(coordinator, sensor_id, name, data_key, UnitOfElectricCurrent.AMPERE)
        self._attr_device_class = SensorDeviceClass.CURRENT
        self._attr_state_class = SensorStateClass.MEASUREMENT


class SPRSUNStatusSensor(CoordinatorEntity, SensorEntity):
    """Status sensor."""

    def __init__(self, coordinator, sensor_id, name, data_key):
        """Initialize the status sensor."""
        super().__init__(coordinator)
        self._sensor_id = sensor_id
        self._attr_name = f"SPRSUN {name}"
        self._attr_unique_id = f"{DOMAIN}_{sensor_id}"
        self._data_key = data_key
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        """Return the state of the sensor."""
        status_code = self.coordinator.data.get(self._data_key)
        if status_code is not None and status_code in STATUS_MAP:
            return STATUS_MAP[status_code]
        return "Unknown"


class SPRSUNCompressorStatusSensor(CoordinatorEntity, SensorEntity):
    """Compressor status sensor."""

    def __init__(self, coordinator, sensor_id, name, data_key):
        """Initialize the compressor status sensor."""
        super().__init__(coordinator)
        self._sensor_id = sensor_id
        self._attr_name = f"SPRSUN {name}"
        self._attr_unique_id = f"{DOMAIN}_{sensor_id}"
        self._data_key = data_key
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        """Return the state of the sensor."""
        status_code = self.coordinator.data.get(self._data_key)
        if status_code is not None and status_code in COMP_STATUS_MAP:
            return COMP_STATUS_MAP[status_code]
        return "Unknown"


class SPRSUNUnitRunModeSensor(CoordinatorEntity, SensorEntity):
    """Unit run mode sensor."""

    def __init__(self, coordinator, sensor_id, name, data_key):
        """Initialize the unit run mode sensor."""
        super().__init__(coordinator)
        self._sensor_id = sensor_id
        self._attr_name = f"SPRSUN {name}"
        self._attr_unique_id = f"{DOMAIN}_{sensor_id}"
        self._data_key = data_key
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        """Return the state of the sensor."""
        mode_code = self.coordinator.data.get(self._data_key)
        if mode_code is not None and mode_code in UNIT_RUN_MODE_MAP:
            return UNIT_RUN_MODE_MAP[mode_code]
        return "Unknown"


class SPRSUNHeaterTypeSensor(CoordinatorEntity, SensorEntity):
    """Heater type sensor."""

    def __init__(self, coordinator, sensor_id, name, data_key):
        """Initialize the heater type sensor."""
        super().__init__(coordinator)
        self._sensor_id = sensor_id
        self._attr_name = f"SPRSUN {name}"
        self._attr_unique_id = f"{DOMAIN}_{sensor_id}"
        self._data_key = data_key
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        """Return the state of the sensor."""
        type_code = self.coordinator.data.get(self._data_key)
        if type_code is not None and type_code in HEATER_TYPE_MAP:
            return HEATER_TYPE_MAP[type_code]
        return "Unknown"


class SPRSUNFlowSensor(SPRSUNSensor):
    """Water flow sensor."""

    def __init__(self, coordinator, sensor_id, name, data_key):
        """Initialize the flow sensor."""
        super().__init__(coordinator, sensor_id, name, data_key, "L/h")
        self._attr_state_class = SensorStateClass.MEASUREMENT


class SPRSUNTimeSensor(SPRSUNSensor):
    """Working hours sensor."""

    def __init__(self, coordinator, sensor_id, name, data_key):
        """Initialize the time sensor."""
        super().__init__(coordinator, sensor_id, name, data_key, UnitOfTime.HOURS)
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_entity_category = EntityCategory.DIAGNOSTIC


class SPRSUNVersionSensor(CoordinatorEntity, SensorEntity):
    """Firmware version sensor (combines X.Y.Z)."""

    def __init__(self, coordinator, sensor_id, name):
        """Initialize the version sensor."""
        super().__init__(coordinator)
        self._sensor_id = sensor_id
        self._attr_name = f"SPRSUN {name}"
        self._attr_unique_id = f"{DOMAIN}_{sensor_id}"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        """Return the firmware version as X.Y.Z."""
        x = self.coordinator.data.get("version_x")
        y = self.coordinator.data.get("version_y")
        z = self.coordinator.data.get("version_z")
        if x is not None and y is not None and z is not None:
            return f"{x}.{y}.{z}"
        return None


class SPRSUNUnitTypeSensor(CoordinatorEntity, SensorEntity):
    """Unit type sensor (combines A.B)."""

    def __init__(self, coordinator, sensor_id, name):
        """Initialize the unit type sensor."""
        super().__init__(coordinator)
        self._sensor_id = sensor_id
        self._attr_name = f"SPRSUN {name}"
        self._attr_unique_id = f"{DOMAIN}_{sensor_id}"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        """Return the unit type as A.B."""
        a = self.coordinator.data.get("unit_type_a")
        b = self.coordinator.data.get("unit_type_b")
        if a is not None and b is not None:
            return f"{a}.{b}"
        return None


class SPRSUNEnergySensor(SPRSUNSensor):
    """Energy sensor (kWh)."""

    def __init__(self, coordinator, sensor_id, name, data_key):
        """Initialize the energy sensor."""
        super().__init__(coordinator, sensor_id, name, data_key, "kWh")
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_entity_category = EntityCategory.DIAGNOSTIC


class SPRSUNSGModeSensor(CoordinatorEntity, SensorEntity):
    """SG Ready mode sensor."""

    def __init__(self, coordinator, sensor_id, name, data_key):
        """Initialize the SG mode sensor."""
        super().__init__(coordinator)
        self._sensor_id = sensor_id
        self._attr_name = f"SPRSUN {name}"
        self._attr_unique_id = f"{DOMAIN}_{sensor_id}"
        self._data_key = data_key
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        """Return the state of the sensor."""
        mode_code = self.coordinator.data.get(self._data_key)
        if mode_code is not None and mode_code in SG_MODE_MAP:
            return SG_MODE_MAP[mode_code]
        return "Unknown"


class SPRSUNWeekdaySensor(CoordinatorEntity, SensorEntity):
    """Weekday sensor."""

    def __init__(self, coordinator, sensor_id, name, data_key):
        """Initialize the weekday sensor."""
        super().__init__(coordinator)
        self._sensor_id = sensor_id
        self._attr_name = f"SPRSUN {name}"
        self._attr_unique_id = f"{DOMAIN}_{sensor_id}"
        self._data_key = data_key
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        """Return the weekday name."""
        weekday_code = self.coordinator.data.get(self._data_key)
        if weekday_code is not None and weekday_code in WEEKDAY_MAP:
            return WEEKDAY_MAP[weekday_code]
        return "Unknown"
