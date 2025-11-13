"""The SPRSUN Heat Pump Modbus integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL, CONF_SLAVE_ID, DEFAULT_SLAVE_ID
from .modbus_client import SPRSUNModbusClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.CLIMATE,
    Platform.SELECT,
    Platform.NUMBER,
    Platform.BINARY_SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SPRSUN Heat Pump Modbus from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Create Modbus client
    client = SPRSUNModbusClient(entry.data)
    
    slave_id = entry.data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)

    async def async_update_data():
        """Fetch data from Modbus."""
        try:
            # Import here to avoid circular imports
            from .const import (
                REG_INLET_TEMP, REG_OUTLET_TEMP, REG_AMBIENT_TEMP,
                REG_HOTWATER_TEMP, REG_STATUS, REG_WORK_MODE, REG_UNIT_RUN_MODE,
                REG_HEATING_SETPOINT, REG_COOLING_SETPOINT, REG_HOTWATER_SETPOINT,
                REG_HW_START_DIFF, REG_HW_STOP_DIFF, REG_CH_START_DIFF, REG_CH_STOP_DIFF,
                REG_FAN_MODE, REG_PUMP_MODE, REG_FAN_OUTPUT, REG_PUMP_OUTPUT,
                REG_REQUIRED_CAP, REG_ACTUAL_CAP, REG_DISCHARGE_TEMP,
                REG_SUCTION_TEMP, REG_DISCHARGE_PRESS, REG_SUCTION_PRESS,
                REG_COIL_TEMP, REG_BLDC_POWER, REG_BLDC_VAR, REG_BLDC_CURRENT,
                REG_EEV_OPENING, REG_COMP_STATUS, REG_COMP_PROTECTION, REG_SUCTION_SH,
                REG_DC_FAN1_OUTPUT, REG_DC_FAN1_FEEDBACK, REG_DC_FAN2_OUTPUT,
                REG_DC_FAN2_FEEDBACK, REG_ACTUAL_SPEED,
                REG_COMP_DELAY, REG_EXT_TEMP_SETP, REG_HEATER_TYPE,
                REG_VERSION_X, REG_VERSION_Y, REG_VERSION_Z, REG_UNIT_TYPE_A, REG_UNIT_TYPE_B,
                REG_WORKING_HOURS_PUMP, REG_WORKING_HOURS_COMP, REG_WORKING_HOURS_FAN, REG_WORKING_HOURS_3WAY,
                REG_WATER_FLOW, REG_UNIT_POWER, REG_UNIT_COP,
                REG_YEAR, REG_MONTH, REG_DAY, REG_HOUR, REG_MINUTE, REG_WEEK,
                REG_PHASE_VOLTAGE_A, REG_PHASE_VOLTAGE_B, REG_PHASE_VOLTAGE_C,
                REG_PHASE_CURRENT_A, REG_PHASE_CURRENT_B, REG_PHASE_CURRENT_C,
                REG_POWER_W, REG_TOTAL_POWER_CONSUMPTION,
                REG_RECORD_POWER_1, REG_RECORD_POWER_2, REG_RECORD_POWER_3, REG_RECORD_POWER_4,
                REG_RECORD_POWER_5, REG_RECORD_POWER_6, REG_RECORD_POWER_7,
                REG_SG_MODE, REG_SG_MODE_CHANGE_HOLDTIME, REG_SG_MODE_W_TANK_SETP,
                REG_SG_COOL_SETP_DIFF_1, REG_SG_HEAT_SETP_DIFF_1, REG_SG_W_TANK_SETP_DIFF_1,
                REG_SG_COOL_SETP_DIFF_2, REG_SG_HEAT_SETP_DIFF_2, REG_SG_W_TANK_SETP_DIFF_2,
                REG_ANTILEG_TEMP_SETP, REG_ANTILEG_WEEKDAY,
                REG_ANTILEG_TIME_START_HR, REG_ANTILEG_TIME_START_MIN,
                REG_ANTILEG_TIME_END_HR, REG_ANTILEG_TIME_END_MIN,
                REG_TZ_TEMP_HR1, REG_TZ_TEMP_MIN1, REG_TZ_S_SET_TEMP1, REG_TZ_W_SET_TEMP1,
                REG_TZ_TEMP_HR2, REG_TZ_TEMP_MIN2, REG_TZ_S_SET_TEMP2, REG_TZ_W_SET_TEMP2,
                REG_TZ_TEMP_HR3, REG_TZ_TEMP_MIN3, REG_TZ_S_SET_TEMP3, REG_TZ_W_SET_TEMP3,
                REG_TZ_TEMP_HR4, REG_TZ_TEMP_MIN4, REG_TZ_S_SET_TEMP4, REG_TZ_W_SET_TEMP4,
                DISCRETE_UNIT_ON, DISCRETE_PUMP, DISCRETE_4WAY_VALVE, DISCRETE_3WAY_VALVE,
                DISCRETE_CRANK_HEATER, DISCRETE_CHASSIS_HEATER, DISCRETE_FLOW_SWITCH,
                DISCRETE_COMP_STATUS, DISCRETE_FAN_STATUS, DISCRETE_SG_SIGNAL, DISCRETE_EVU_SIGNAL,
                DISCRETE_DOUT_VAL_1, DISCRETE_DOUT_VAL_9, DISCRETE_AC_LINKAGE,
                COIL_FAN_LOW,  # Legacy - not in manufacturer table
                COIL_COOLING_LINKAGE, COIL_HEATING_LINKAGE, COIL_TERMINAL_PUMP
            )

            data = {}

            # Read temperatures
            data["inlet_temp"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_INLET_TEMP, 1, 1, slave_id
            )
            data["outlet_temp"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_OUTLET_TEMP, 1, 1, slave_id
            )
            data["ambient_temp"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_AMBIENT_TEMP, 1, 1, slave_id
            )
            data["hotwater_temp"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_HOTWATER_TEMP, 1, 1, slave_id
            )
            data["discharge_temp"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_DISCHARGE_TEMP, 1, 1, slave_id
            )
            data["suction_temp"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_SUCTION_TEMP, 1, 1, slave_id
            )
            data["coil_temp"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_COIL_TEMP, 1, 1, slave_id
            )
            data["suction_sh"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_SUCTION_SH, 1, 1, slave_id
            )

            # Read pressures
            data["discharge_press"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_DISCHARGE_PRESS, 1, 1, slave_id
            )
            data["suction_press"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_SUCTION_PRESS, 1, 1, slave_id
            )

            # Read status and modes
            data["status"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_STATUS, 1, 0, slave_id
            )
            data["work_mode"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_WORK_MODE, 1, 0, slave_id
            )
            data["unit_run_mode"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_UNIT_RUN_MODE, 1, 0, slave_id
            )
            data["fan_mode"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_FAN_MODE, 1, 0, slave_id
            )
            data["pump_mode"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_PUMP_MODE, 1, 0, slave_id
            )

            # Read setpoints
            data["heating_setpoint"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_HEATING_SETPOINT, 1, 1, slave_id
            )
            data["cooling_setpoint"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_COOLING_SETPOINT, 1, 1, slave_id
            )
            data["hotwater_setpoint"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_HOTWATER_SETPOINT, 1, 1, slave_id
            )

            # Read differential settings
            data["hw_start_diff"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_HW_START_DIFF, 1, 1, slave_id
            )
            data["hw_stop_diff"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_HW_STOP_DIFF, 1, 1, slave_id
            )
            data["ch_start_diff"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_CH_START_DIFF, 1, 1, slave_id
            )
            data["ch_stop_diff"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_CH_STOP_DIFF, 1, 1, slave_id
            )

            # Read engineering parameters
            data["comp_delay"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_COMP_DELAY, 1, 0, slave_id
            )
            data["ext_temp_setp"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_EXT_TEMP_SETP, 1, 1, slave_id
            )
            data["heater_type"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_HEATER_TYPE, 1, 0, slave_id
            )

            # Read outputs
            data["fan_output"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_FAN_OUTPUT, 1, 1, slave_id
            )
            data["pump_output"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_PUMP_OUTPUT, 1, 1, slave_id
            )
            data["dc_fan1_output"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_DC_FAN1_OUTPUT, 1, 1, slave_id
            )
            data["dc_fan1_feedback"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_DC_FAN1_FEEDBACK, 1, 0, slave_id
            )
            data["dc_fan2_output"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_DC_FAN2_OUTPUT, 1, 1, slave_id
            )
            data["dc_fan2_feedback"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_DC_FAN2_FEEDBACK, 1, 0, slave_id
            )
            data["required_cap"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_REQUIRED_CAP, 1, 1, slave_id
            )
            data["actual_cap"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_ACTUAL_CAP, 1, 1, slave_id
            )
            data["actual_speed"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_ACTUAL_SPEED, 1, 0, slave_id
            )
            data["eev_opening"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_EEV_OPENING, 1, 0, slave_id
            )
            data["comp_status"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_COMP_STATUS, 1, 0, slave_id
            )
            data["comp_protection"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_COMP_PROTECTION, 1, 0, slave_id
            )

            # Read version and unit type
            data["version_x"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_VERSION_X, 1, 0, slave_id
            )
            data["version_y"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_VERSION_Y, 1, 0, slave_id
            )
            data["version_z"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_VERSION_Z, 1, 0, slave_id
            )
            data["unit_type_a"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_UNIT_TYPE_A, 1, 0, slave_id
            )
            data["unit_type_b"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_UNIT_TYPE_B, 1, 0, slave_id
            )

            # Read BLDC motor data
            data["bldc_power"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_BLDC_POWER, 1, 1, slave_id
            )
            data["bldc_var"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_BLDC_VAR, 1, 0, slave_id
            )
            data["bldc_current"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_BLDC_CURRENT, 1, 1, slave_id
            )

            # Read working hours (32-bit registers)
            data["working_hours_pump"] = await hass.async_add_executor_job(
                client.read_holding_register_32bit, REG_WORKING_HOURS_PUMP, 0, slave_id
            )
            data["working_hours_comp"] = await hass.async_add_executor_job(
                client.read_holding_register_32bit, REG_WORKING_HOURS_COMP, 0, slave_id
            )
            data["working_hours_fan"] = await hass.async_add_executor_job(
                client.read_holding_register_32bit, REG_WORKING_HOURS_FAN, 0, slave_id
            )
            data["working_hours_3way"] = await hass.async_add_executor_job(
                client.read_holding_register_32bit, REG_WORKING_HOURS_3WAY, 0, slave_id
            )

            # Read water flow and power (32-bit float32 registers)
            data["water_flow"] = await hass.async_add_executor_job(
                client.read_holding_register_float32, REG_WATER_FLOW, slave_id
            )
            data["unit_power"] = await hass.async_add_executor_job(
                client.read_holding_register_float32, REG_UNIT_POWER, slave_id
            )

            # Read COP
            data["unit_cop"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_UNIT_COP, 1, 1, slave_id
            )

            # Read time setting
            data["year"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_YEAR, 1, 0, slave_id
            )
            data["month"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_MONTH, 1, 0, slave_id
            )
            data["day"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_DAY, 1, 0, slave_id
            )
            data["hour"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_HOUR, 1, 0, slave_id
            )
            data["minute"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_MINUTE, 1, 0, slave_id
            )
            data["week"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_WEEK, 1, 0, slave_id
            )

            # Read Electric Meter
            data["phase_voltage_a"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_PHASE_VOLTAGE_A, 1, 1, slave_id
            )
            data["phase_voltage_b"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_PHASE_VOLTAGE_B, 1, 1, slave_id
            )
            data["phase_voltage_c"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_PHASE_VOLTAGE_C, 1, 1, slave_id
            )
            data["phase_current_a"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_PHASE_CURRENT_A, 1, 1, slave_id
            )
            data["phase_current_b"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_PHASE_CURRENT_B, 1, 1, slave_id
            )
            data["phase_current_c"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_PHASE_CURRENT_C, 1, 1, slave_id
            )
            data["power_w"] = await hass.async_add_executor_job(
                client.read_holding_register_float32, REG_POWER_W, slave_id
            )
            data["total_power_consumption"] = await hass.async_add_executor_job(
                client.read_holding_register_float32, REG_TOTAL_POWER_CONSUMPTION, slave_id
            )
            data["record_power_1"] = await hass.async_add_executor_job(
                client.read_holding_register_float32, REG_RECORD_POWER_1, slave_id
            )
            data["record_power_2"] = await hass.async_add_executor_job(
                client.read_holding_register_float32, REG_RECORD_POWER_2, slave_id
            )
            data["record_power_3"] = await hass.async_add_executor_job(
                client.read_holding_register_float32, REG_RECORD_POWER_3, slave_id
            )
            data["record_power_4"] = await hass.async_add_executor_job(
                client.read_holding_register_float32, REG_RECORD_POWER_4, slave_id
            )
            data["record_power_5"] = await hass.async_add_executor_job(
                client.read_holding_register_float32, REG_RECORD_POWER_5, slave_id
            )
            data["record_power_6"] = await hass.async_add_executor_job(
                client.read_holding_register_float32, REG_RECORD_POWER_6, slave_id
            )
            data["record_power_7"] = await hass.async_add_executor_job(
                client.read_holding_register_float32, REG_RECORD_POWER_7, slave_id
            )

            # Read SG Ready
            data["sg_mode"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_SG_MODE, 1, 0, slave_id
            )
            data["sg_mode_change_holdtime"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_SG_MODE_CHANGE_HOLDTIME, 1, 0, slave_id
            )
            data["sg_mode_w_tank_setp"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_SG_MODE_W_TANK_SETP, 1, 1, slave_id
            )
            data["sg_cool_setp_diff_1"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_SG_COOL_SETP_DIFF_1, 1, 1, slave_id
            )
            data["sg_heat_setp_diff_1"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_SG_HEAT_SETP_DIFF_1, 1, 1, slave_id
            )
            data["sg_w_tank_setp_diff_1"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_SG_W_TANK_SETP_DIFF_1, 1, 1, slave_id
            )
            data["sg_cool_setp_diff_2"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_SG_COOL_SETP_DIFF_2, 1, 1, slave_id
            )
            data["sg_heat_setp_diff_2"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_SG_HEAT_SETP_DIFF_2, 1, 1, slave_id
            )
            data["sg_w_tank_setp_diff_2"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_SG_W_TANK_SETP_DIFF_2, 1, 1, slave_id
            )

            # Read Timezone temperature settings
            data["tz_temp_hr1"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_TZ_TEMP_HR1, 1, 0, slave_id
            )
            data["tz_temp_min1"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_TZ_TEMP_MIN1, 1, 0, slave_id
            )
            data["tz_s_set_temp1"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_TZ_S_SET_TEMP1, 1, 1, slave_id
            )
            data["tz_w_set_temp1"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_TZ_W_SET_TEMP1, 1, 1, slave_id
            )
            data["tz_temp_hr2"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_TZ_TEMP_HR2, 1, 0, slave_id
            )
            data["tz_temp_min2"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_TZ_TEMP_MIN2, 1, 0, slave_id
            )
            data["tz_s_set_temp2"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_TZ_S_SET_TEMP2, 1, 1, slave_id
            )
            data["tz_w_set_temp2"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_TZ_W_SET_TEMP2, 1, 1, slave_id
            )
            data["tz_temp_hr3"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_TZ_TEMP_HR3, 1, 0, slave_id
            )
            data["tz_temp_min3"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_TZ_TEMP_MIN3, 1, 0, slave_id
            )
            data["tz_s_set_temp3"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_TZ_S_SET_TEMP3, 1, 1, slave_id
            )
            data["tz_w_set_temp3"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_TZ_W_SET_TEMP3, 1, 1, slave_id
            )
            data["tz_temp_hr4"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_TZ_TEMP_HR4, 1, 0, slave_id
            )
            data["tz_temp_min4"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_TZ_TEMP_MIN4, 1, 0, slave_id
            )
            data["tz_s_set_temp4"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_TZ_S_SET_TEMP4, 1, 1, slave_id
            )
            data["tz_w_set_temp4"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_TZ_W_SET_TEMP4, 1, 1, slave_id
            )

            # Read Timezone1 and Timezone2 schedulers
            # Timezone1: Mon-Sun ON/OFF hours and minutes (40219-40246)
            # Timezone2: Mon-Sun ON/OFF hours and minutes (40433-40460)
            from . import const as const_module
            timezone_days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
            for tz_num in [1, 2]:
                for day in timezone_days:
                    for time_type in ["ON", "OFF"]:
                        # Read hour
                        reg_name_hr = f"REG_TZ{tz_num}_{day}_{time_type}_HOUR"
                        register_hr = getattr(const_module, reg_name_hr)
                        data_key_hr = f"tz{tz_num}_{day.lower()}_{time_type.lower()}_hour"
                        data[data_key_hr] = await hass.async_add_executor_job(
                            client.read_holding_register, register_hr, 1, 0, slave_id
                        )

                        # Read minute
                        reg_name_min = f"REG_TZ{tz_num}_{day}_{time_type}_MIN"
                        register_min = getattr(const_module, reg_name_min)
                        data_key_min = f"tz{tz_num}_{day.lower()}_{time_type.lower()}_min"
                        data[data_key_min] = await hass.async_add_executor_job(
                            client.read_holding_register, register_min, 1, 0, slave_id
                        )

            # Read Anti-legionella
            data["antileg_temp_setp"] = await hass.async_add_executor_job(
                client.read_holding_register_float32, REG_ANTILEG_TEMP_SETP, slave_id
            )
            data["antileg_weekday"] = await hass.async_add_executor_job(
                client.read_holding_register, REG_ANTILEG_WEEKDAY, 1, 0, slave_id
            )
            # Combine hours and minutes into time string
            start_hr = await hass.async_add_executor_job(
                client.read_holding_register, REG_ANTILEG_TIME_START_HR, 1, 0, slave_id
            )
            start_min = await hass.async_add_executor_job(
                client.read_holding_register, REG_ANTILEG_TIME_START_MIN, 1, 0, slave_id
            )
            if start_hr is not None and start_min is not None:
                data["antileg_time_start"] = f"{int(start_hr):02d}:{int(start_min):02d}"
            else:
                data["antileg_time_start"] = None

            end_hr = await hass.async_add_executor_job(
                client.read_holding_register, REG_ANTILEG_TIME_END_HR, 1, 0, slave_id
            )
            end_min = await hass.async_add_executor_job(
                client.read_holding_register, REG_ANTILEG_TIME_END_MIN, 1, 0, slave_id
            )
            if end_hr is not None and end_min is not None:
                data["antileg_time_end"] = f"{int(end_hr):02d}:{int(end_min):02d}"
            else:
                data["antileg_time_end"] = None

            # Read discrete inputs (status - read only)
            # Unit On/OFF is read-only status at discrete input 10001 (address 0)
            data["unit_on"] = await hass.async_add_executor_job(
                client.read_discrete_input, DISCRETE_UNIT_ON, slave_id
            )
            data["pump"] = await hass.async_add_executor_job(
                client.read_discrete_input, DISCRETE_PUMP, slave_id
            )
            data["flow_switch"] = await hass.async_add_executor_job(
                client.read_discrete_input, DISCRETE_FLOW_SWITCH, slave_id
            )
            data["ac_linkage"] = await hass.async_add_executor_job(
                client.read_discrete_input, DISCRETE_AC_LINKAGE, slave_id
            )
            data["sg_signal"] = await hass.async_add_executor_job(
                client.read_discrete_input, DISCRETE_SG_SIGNAL, slave_id
            )
            data["dout_val_1"] = await hass.async_add_executor_job(
                client.read_discrete_input, DISCRETE_DOUT_VAL_1, slave_id
            )
            data["4way_valve"] = await hass.async_add_executor_job(
                client.read_discrete_input, DISCRETE_4WAY_VALVE, slave_id
            )
            data["three_valve"] = await hass.async_add_executor_job(
                client.read_discrete_input, DISCRETE_3WAY_VALVE, slave_id
            )
            data["crank_heater"] = await hass.async_add_executor_job(
                client.read_discrete_input, DISCRETE_CRANK_HEATER, slave_id
            )
            data["chassis_heater"] = await hass.async_add_executor_job(
                client.read_discrete_input, DISCRETE_CHASSIS_HEATER, slave_id
            )
            data["dout_val_9"] = await hass.async_add_executor_job(
                client.read_discrete_input, DISCRETE_DOUT_VAL_9, slave_id
            )
            data["comp_on"] = await hass.async_add_executor_job(
                client.read_discrete_input, DISCRETE_COMP_STATUS, slave_id
            )
            data["fan_on"] = await hass.async_add_executor_job(
                client.read_discrete_input, DISCRETE_FAN_STATUS, slave_id
            )
            data["evu_signal"] = await hass.async_add_executor_job(
                client.read_discrete_input, DISCRETE_EVU_SIGNAL, slave_id
            )
            # Linkage sensors
            data["cooling_linkage"] = await hass.async_add_executor_job(
                client.read_discrete_input, COIL_COOLING_LINKAGE, slave_id
            )
            data["heating_linkage"] = await hass.async_add_executor_job(
                client.read_discrete_input, COIL_HEATING_LINKAGE, slave_id
            )
            data["terminal_pump"] = await hass.async_add_executor_job(
                client.read_discrete_input, COIL_TERMINAL_PUMP, slave_id
            )
            # Legacy compatibility
            data["fan_high"] = data.get("dout_val_1")
            data["fan_low"] = await hass.async_add_executor_job(
                client.read_discrete_input, COIL_FAN_LOW, slave_id
            )
            data["heater"] = data.get("dout_val_9")

            # Read alarms (all - AL001 to AL177)
            # According to manufacturer table: discrete inputs 10014-10189 (addresses 13-188)
            for alarm_reg in range(13, 189):  # All alarms from manufacturer table
                data[f"alarm_{alarm_reg}"] = await hass.async_add_executor_job(
                    client.read_discrete_input, alarm_reg, slave_id
                )

            return data

        except Exception as err:
            raise UpdateFailed(f"Error communicating with device: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
    )

    # Nastavení kritických parametrů při startu integrace
    _LOGGER.info("Nastavení kritických parametrů tepelného čerpadla...")
    
    from .const import (
        REG_PUMP_MODE, PUMP_MODE_ALWAYS,
        REG_PUMP_START_INTERVAL, REG_COMP_DELAY
    )
    
    try:
        # 1. Nastavení Pump Mode na Always
        success = await hass.async_add_executor_job(
            client.write_register,
            REG_PUMP_MODE,
            PUMP_MODE_ALWAYS,  # 3 = Always
            0,
            slave_id
        )
        if success:
            _LOGGER.info("Pump Mode nastaven na Always")
        else:
            _LOGGER.warning("Nepodařilo se nastavit Pump Mode na Always")
        
        # 2. Nastavení Pump Start Interval na 3 minuty
        success = await hass.async_add_executor_job(
            client.write_register,
            REG_PUMP_START_INTERVAL,
            3,  # 3 minuty
            0,
            slave_id
        )
        if success:
            _LOGGER.info("Pump Start Interval nastaven na 3 minuty")
        else:
            _LOGGER.warning("Nepodařilo se nastavit Pump Start Interval")
        
        # 3. Nastavení Compressor Delay na 50 sekund
        success = await hass.async_add_executor_job(
            client.write_register,
            REG_COMP_DELAY,
            50,  # 50 sekund
            0,
            slave_id
        )
        if success:
            _LOGGER.info("Compressor Delay nastaven na 50 sekund")
        else:
            _LOGGER.warning("Nepodařilo se nastavit Compressor Delay")
            
    except Exception as err:
        _LOGGER.error(f"Chyba při nastavování kritických parametrů: {err}")

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "client": client,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        data = hass.data[DOMAIN].pop(entry.entry_id)
        await hass.async_add_executor_job(data["client"].close)

    return unload_ok
