"""Number platform for SPRSUN Heat Pump Modbus."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import const

DOMAIN = const.DOMAIN
CONF_SLAVE_ID = const.CONF_SLAVE_ID
DEFAULT_SLAVE_ID = const.DEFAULT_SLAVE_ID

_LOGGER = logging.getLogger(__name__)

# Timezone scheduler days configuration
TIMEZONE_DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
TIMEZONE_DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SPRSUN number entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][entry.entry_id]["client"]
    slave_id = entry.data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)

    numbers = [
        # Hlavní setpointy - viditelné v Controls sekci
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "heating_setpoint",
            "Heating Setpoint",
            const.REG_HEATING_SETPOINT,
            "heating_setpoint",
            10.0,
            70.0,
            0.5,
            UnitOfTemperature.CELSIUS,
            1,
            entity_category=None,  # Viditelné v Controls
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "cooling_setpoint",
            "Cooling Setpoint",
            const.REG_COOLING_SETPOINT,
            "cooling_setpoint",
            10.0,
            40.0,
            0.5,
            UnitOfTemperature.CELSIUS,
            1,
            entity_category=None,  # Viditelné v Controls
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "hotwater_setpoint",
            "Hot Water Setpoint",
            const.REG_HOTWATER_SETPOINT,
            "hotwater_setpoint",
            10.0,
            70.0,
            0.5,
            UnitOfTemperature.CELSIUS,
            1,
            entity_category=None,  # Viditelné v Controls
        ),
        # Differenciály - skryté v Configuration sekci (výchozí entity_category=CONFIG)
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "hw_start_diff",
            "Hot Water Start Differential",
            const.REG_HW_START_DIFF,
            "hw_start_diff",
            1.0,
            15.0,
            0.5,
            UnitOfTemperature.CELSIUS,
            1,
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "hw_stop_diff",
            "Hot Water Stop Differential",
            const.REG_HW_STOP_DIFF,
            "hw_stop_diff",
            0.0,
            5.0,
            0.5,
            UnitOfTemperature.CELSIUS,
            1,
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "ch_start_diff",
            "Heating/Cooling Start Differential",
            const.REG_CH_START_DIFF,
            "ch_start_diff",
            1.0,
            15.0,
            0.5,
            UnitOfTemperature.CELSIUS,
            1,
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "ch_stop_diff",
            "Heating/Cooling Stop Differential",
            const.REG_CH_STOP_DIFF,
            "ch_stop_diff",
            0.0,
            5.0,
            0.5,
            UnitOfTemperature.CELSIUS,
            1,
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "comp_delay",
            "Compressor Delay",
            const.REG_COMP_DELAY,
            "comp_delay",
            0,
            999,
            1,
            "s",
            0,
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "ext_temp_setp",
            "External Temperature Setpoint",
            const.REG_EXT_TEMP_SETP,
            "ext_temp_setp",
            -30.0,
            20.0,
            0.5,
            UnitOfTemperature.CELSIUS,
            1,
        ),
        # SG Ready differential settings
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "sg_cool_setp_diff_1",
            "SG Cool Setpoint Differential 1",
            const.REG_SG_COOL_SETP_DIFF_1,
            "sg_cool_setp_diff_1",
            0.0,
            10.0,
            0.5,
            UnitOfTemperature.CELSIUS,
            1,
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "sg_heat_setp_diff_1",
            "SG Heat Setpoint Differential 1",
            const.REG_SG_HEAT_SETP_DIFF_1,
            "sg_heat_setp_diff_1",
            0.0,
            10.0,
            0.5,
            UnitOfTemperature.CELSIUS,
            1,
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "sg_w_tank_setp_diff_1",
            "SG Water Tank Setpoint Differential 1",
            const.REG_SG_W_TANK_SETP_DIFF_1,
            "sg_w_tank_setp_diff_1",
            0.0,
            10.0,
            0.5,
            UnitOfTemperature.CELSIUS,
            1,
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "sg_cool_setp_diff_2",
            "SG Cool Setpoint Differential 2",
            const.REG_SG_COOL_SETP_DIFF_2,
            "sg_cool_setp_diff_2",
            0.0,
            10.0,
            0.5,
            UnitOfTemperature.CELSIUS,
            1,
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "sg_heat_setp_diff_2",
            "SG Heat Setpoint Differential 2",
            const.REG_SG_HEAT_SETP_DIFF_2,
            "sg_heat_setp_diff_2",
            0.0,
            10.0,
            0.5,
            UnitOfTemperature.CELSIUS,
            1,
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "sg_w_tank_setp_diff_2",
            "SG Water Tank Setpoint Differential 2",
            const.REG_SG_W_TANK_SETP_DIFF_2,
            "sg_w_tank_setp_diff_2",
            0.0,
            10.0,
            0.5,
            UnitOfTemperature.CELSIUS,
            1,
        ),
        # Timezone temperature settings
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "tz_temp_hr1",
            "Timezone Temperature Hour 1",
            const.REG_TZ_TEMP_HR1,
            "tz_temp_hr1",
            0,
            23,
            1,
            "h",
            0,
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "tz_temp_min1",
            "Timezone Temperature Minute 1",
            const.REG_TZ_TEMP_MIN1,
            "tz_temp_min1",
            0,
            59,
            1,
            "min",
            0,
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "tz_s_set_temp1",
            "Timezone S Set Temperature 1",
            const.REG_TZ_S_SET_TEMP1,
            "tz_s_set_temp1",
            -99.0,
            99.0,
            0.5,
            UnitOfTemperature.CELSIUS,
            1,
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "tz_w_set_temp1",
            "Timezone W Set Temperature 1",
            const.REG_TZ_W_SET_TEMP1,
            "tz_w_set_temp1",
            -99.0,
            99.0,
            0.5,
            UnitOfTemperature.CELSIUS,
            1,
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "tz_temp_hr2",
            "Timezone Temperature Hour 2",
            const.REG_TZ_TEMP_HR2,
            "tz_temp_hr2",
            0,
            23,
            1,
            "h",
            0,
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "tz_temp_min2",
            "Timezone Temperature Minute 2",
            const.REG_TZ_TEMP_MIN2,
            "tz_temp_min2",
            0,
            59,
            1,
            "min",
            0,
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "tz_s_set_temp2",
            "Timezone S Set Temperature 2",
            const.REG_TZ_S_SET_TEMP2,
            "tz_s_set_temp2",
            -99.0,
            99.0,
            0.5,
            UnitOfTemperature.CELSIUS,
            1,
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "tz_w_set_temp2",
            "Timezone W Set Temperature 2",
            const.REG_TZ_W_SET_TEMP2,
            "tz_w_set_temp2",
            -99.0,
            99.0,
            0.5,
            UnitOfTemperature.CELSIUS,
            1,
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "tz_temp_hr3",
            "Timezone Temperature Hour 3",
            const.REG_TZ_TEMP_HR3,
            "tz_temp_hr3",
            0,
            23,
            1,
            "h",
            0,
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "tz_temp_min3",
            "Timezone Temperature Minute 3",
            const.REG_TZ_TEMP_MIN3,
            "tz_temp_min3",
            0,
            59,
            1,
            "min",
            0,
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "tz_s_set_temp3",
            "Timezone S Set Temperature 3",
            const.REG_TZ_S_SET_TEMP3,
            "tz_s_set_temp3",
            -99.0,
            99.0,
            0.5,
            UnitOfTemperature.CELSIUS,
            1,
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "tz_w_set_temp3",
            "Timezone W Set Temperature 3",
            const.REG_TZ_W_SET_TEMP3,
            "tz_w_set_temp3",
            -99.0,
            99.0,
            0.5,
            UnitOfTemperature.CELSIUS,
            1,
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "tz_temp_hr4",
            "Timezone Temperature Hour 4",
            const.REG_TZ_TEMP_HR4,
            "tz_temp_hr4",
            0,
            23,
            1,
            "h",
            0,
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "tz_temp_min4",
            "Timezone Temperature Minute 4",
            const.REG_TZ_TEMP_MIN4,
            "tz_temp_min4",
            0,
            59,
            1,
            "min",
            0,
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "tz_s_set_temp4",
            "Timezone S Set Temperature 4",
            const.REG_TZ_S_SET_TEMP4,
            "tz_s_set_temp4",
            -99.0,
            99.0,
            0.5,
            UnitOfTemperature.CELSIUS,
            1,
        ),
        SPRSUNNumber(
            coordinator,
            client,
            slave_id,
            "tz_w_set_temp4",
            "Timezone W Set Temperature 4",
            const.REG_TZ_W_SET_TEMP4,
            "tz_w_set_temp4",
            -99.0,
            99.0,
            0.5,
            UnitOfTemperature.CELSIUS,
            1,
        ),
    ]

    # Add Timezone1 and Timezone2 scheduler entities dynamically
    for tz_num in [1, 2]:
        for day_idx, (day, day_name) in enumerate(zip(TIMEZONE_DAYS, TIMEZONE_DAY_NAMES)):
            for time_type, time_name in [("ON", "On"), ("OFF", "Off")]:
                # Hour entity
                reg_name_hr = f"REG_TZ{tz_num}_{day}_{time_type}_HOUR"
                register_hr = getattr(const, reg_name_hr)
                numbers.append(SPRSUNNumber(
                    coordinator,
                    client,
                    slave_id,
                    f"tz{tz_num}_{day.lower()}_{time_type.lower()}_hour",
                    f"Timezone{tz_num} {day_name} {time_name} Hour",
                    register_hr,
                    f"tz{tz_num}_{day.lower()}_{time_type.lower()}_hour",
                    0,
                    23,
                    1,
                    "h",
                    0,
                ))

                # Minute entity
                reg_name_min = f"REG_TZ{tz_num}_{day}_{time_type}_MIN"
                register_min = getattr(const, reg_name_min)
                numbers.append(SPRSUNNumber(
                    coordinator,
                    client,
                    slave_id,
                    f"tz{tz_num}_{day.lower()}_{time_type.lower()}_min",
                    f"Timezone{tz_num} {day_name} {time_name} Minute",
                    register_min,
                    f"tz{tz_num}_{day.lower()}_{time_type.lower()}_min",
                    0,
                    59,
                    1,
                    "min",
                    0,
                ))

    async_add_entities(numbers)


class SPRSUNNumber(CoordinatorEntity, NumberEntity):
    """SPRSUN Heat Pump number entity."""

    _attr_mode = NumberMode.BOX

    def __init__(
        self,
        coordinator,
        client,
        slave_id,
        number_id,
        name,
        register,
        data_key,
        min_value,
        max_value,
        step,
        unit,
        decimal_places,
        entity_category=EntityCategory.CONFIG,
    ):
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._client = client
        self._slave_id = slave_id
        self._number_id = number_id
        self._attr_name = f"SPRSUN {name}"
        self._attr_unique_id = f"{DOMAIN}_{number_id}"
        self._register = register
        self._data_key = data_key
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
        self._attr_native_step = step
        self._attr_native_unit_of_measurement = unit
        self._decimal_places = decimal_places
        self._attr_entity_category = entity_category

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self.coordinator.data.get(self._data_key)

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        success = await self.hass.async_add_executor_job(
            self._client.write_register,
            self._register,
            value,
            self._decimal_places,
            self._slave_id,
        )

        if success:
            await self.coordinator.async_request_refresh()
