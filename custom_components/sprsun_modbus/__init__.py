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
        """Fetch data from Modbus using optimized bulk reads."""
        try:
            from .const import (
                REG_WORK_MODE, REG_YEAR, REG_INLET_TEMP, REG_UNIT_RUN_MODE,
                REG_TZ_TEMP_HR1, REG_HEATER_TYPE, REG_VERSION_X, REG_BLDC_POWER,
                REG_SG_MODE, REG_WORKING_HOURS_PUMP, REG_WATER_FLOW,
                REG_RECORD_POWER_1, REG_ANTILEG_TEMP_SETP,
                DISCRETE_UNIT_ON, DISCRETE_PUMP, DISCRETE_4WAY_VALVE, DISCRETE_3WAY_VALVE,
                DISCRETE_CRANK_HEATER, DISCRETE_CHASSIS_HEATER, DISCRETE_FLOW_SWITCH,
                DISCRETE_COMP_STATUS, DISCRETE_FAN_STATUS, DISCRETE_SG_SIGNAL, DISCRETE_EVU_SIGNAL,
                DISCRETE_DOUT_VAL_1, DISCRETE_DOUT_VAL_9, DISCRETE_AC_LINKAGE,
                COIL_FAN_LOW, COIL_COOLING_LINKAGE, COIL_HEATING_LINKAGE, COIL_TERMINAL_PUMP
            )

            data = {}

            # ========== BULK READ 1: Control registers (0-14) - 15 registers ==========
            control_regs = await hass.async_add_executor_job(
                client.read_holding_registers_bulk, 0, 15, 0, slave_id
            )
            if control_regs and len(control_regs) == 15:
                data["work_mode"] = control_regs[0]
                data["heating_setpoint"] = float(control_regs[1] / 10) if control_regs[1] is not None else None
                data["cooling_setpoint"] = float(control_regs[2] / 10) if control_regs[2] is not None else None
                data["hotwater_setpoint"] = float(control_regs[3] / 10) if control_regs[3] is not None else None
                data["hw_start_diff"] = float(control_regs[4] / 10) if control_regs[4] is not None else None
                data["hw_stop_diff"] = float(control_regs[5] / 10) if control_regs[5] is not None else None
                data["ch_start_diff"] = float(control_regs[6] / 10) if control_regs[6] is not None else None
                data["ch_stop_diff"] = float(control_regs[7] / 10) if control_regs[7] is not None else None
                # register 8 is pump_start_interval - not used in sensors
                data["pump_mode"] = control_regs[11]
                data["fan_mode"] = control_regs[12]
                data["comp_delay"] = control_regs[13]
                data["ext_temp_setp"] = float(control_regs[14] / 10) if control_regs[14] is not None else None

            # ========== BULK READ 2: Time registers (182-187) - 6 registers ==========
            time_regs = await hass.async_add_executor_job(
                client.read_holding_registers_bulk, REG_YEAR, 6, 0, slave_id
            )
            if time_regs and len(time_regs) == 6:
                data["year"] = time_regs[0]
                data["month"] = time_regs[1]
                data["day"] = time_regs[2]
                data["hour"] = time_regs[3]
                data["minute"] = time_regs[4]
                data["week"] = time_regs[5]

            # ========== BULK READ 3: Main sensors block (188-211) - 24 registers ==========
            sensors_regs = await hass.async_add_executor_job(
                client.read_holding_registers_bulk, REG_INLET_TEMP, 24, 1, slave_id
            )
            if sensors_regs and len(sensors_regs) == 24:
                data["inlet_temp"] = sensors_regs[0]  # 188
                data["outlet_temp"] = sensors_regs[1]  # 189
                data["ambient_temp"] = sensors_regs[2]  # 190
                data["discharge_temp"] = sensors_regs[3]  # 191
                data["suction_temp"] = sensors_regs[4]  # 192
                data["discharge_press"] = sensors_regs[5]  # 193
                data["suction_press"] = sensors_regs[6]  # 194
                data["hotwater_temp"] = sensors_regs[7]  # 195
                data["coil_temp"] = sensors_regs[8]  # 196
                data["fan_output"] = sensors_regs[9]  # 197
                data["pump_output"] = sensors_regs[10]  # 198
                data["dc_fan1_output"] = sensors_regs[11]  # 199
                # Convert fan feedbacks from raw to int (no decimal for RPM/counts)
                data["dc_fan1_feedback"] = int(sensors_regs[12] * 10) if sensors_regs[12] is not None else None  # 200
                data["dc_fan2_output"] = sensors_regs[13]  # 201
                data["dc_fan2_feedback"] = int(sensors_regs[14] * 10) if sensors_regs[14] is not None else None  # 202
                data["required_cap"] = sensors_regs[15]  # 203
                data["actual_cap"] = sensors_regs[16]  # 204
                data["actual_speed"] = int(sensors_regs[17] * 10) if sensors_regs[17] is not None else None  # 205
                # 206 is reserved
                data["eev_opening"] = int(sensors_regs[19] * 10) if sensors_regs[19] is not None else None  # 207
                # 208 is reserved
                data["comp_status"] = int(sensors_regs[21] * 10) if sensors_regs[21] is not None else None  # 209
                data["comp_protection"] = int(sensors_regs[22] * 10) if sensors_regs[22] is not None else None  # 210
                data["suction_sh"] = sensors_regs[23]  # 211

            # ========== BULK READ 4: Status registers (215-217) - 3 registers ==========
            status_regs = await hass.async_add_executor_job(
                client.read_holding_registers_bulk, REG_UNIT_RUN_MODE, 3, 0, slave_id
            )
            if status_regs and len(status_regs) == 3:
                data["unit_run_mode"] = status_regs[0]  # 215
                # 216 is reserved
                data["status"] = status_regs[2]  # 217

            # ========== BULK READ 5: Timezone temperature settings (246-261) - 16 registers ==========
            tz_temp_regs = await hass.async_add_executor_job(
                client.read_holding_registers_bulk, REG_TZ_TEMP_HR1, 16, 0, slave_id
            )
            if tz_temp_regs and len(tz_temp_regs) == 16:
                # Time values (no decimal)
                for i, key in enumerate(["tz_temp_hr1", "tz_temp_min1", "tz_temp_hr2", "tz_temp_min2",
                                         "tz_temp_hr3", "tz_temp_min3", "tz_temp_hr4", "tz_temp_min4"]):
                    if i in [0, 1, 4, 5, 8, 9, 12, 13]:  # hour/minute indices
                        data[key] = tz_temp_regs[i]
                # Temperature values (1 decimal place)
                data["tz_s_set_temp1"] = float(tz_temp_regs[2] / 10) if tz_temp_regs[2] is not None else None
                data["tz_w_set_temp1"] = float(tz_temp_regs[3] / 10) if tz_temp_regs[3] is not None else None
                data["tz_s_set_temp2"] = float(tz_temp_regs[6] / 10) if tz_temp_regs[6] is not None else None
                data["tz_w_set_temp2"] = float(tz_temp_regs[7] / 10) if tz_temp_regs[7] is not None else None
                data["tz_s_set_temp3"] = float(tz_temp_regs[10] / 10) if tz_temp_regs[10] is not None else None
                data["tz_w_set_temp3"] = float(tz_temp_regs[11] / 10) if tz_temp_regs[11] is not None else None
                data["tz_s_set_temp4"] = float(tz_temp_regs[14] / 10) if tz_temp_regs[14] is not None else None
                data["tz_w_set_temp4"] = float(tz_temp_regs[15] / 10) if tz_temp_regs[15] is not None else None

            # ========== BULK READ 6: Heater type (323) - 1 register ==========
            heater_type = await hass.async_add_executor_job(
                client.read_holding_register, REG_HEATER_TYPE, 1, 0, slave_id
            )
            data["heater_type"] = heater_type

            # ========== BULK READ 7: Version and Unit Type (325-329) - 5 registers ==========
            version_regs = await hass.async_add_executor_job(
                client.read_holding_registers_bulk, REG_VERSION_X, 5, 0, slave_id
            )
            if version_regs and len(version_regs) == 5:
                data["version_x"] = version_regs[0]
                data["version_y"] = version_regs[1]
                data["version_z"] = version_regs[2]
                data["unit_type_a"] = version_regs[3]
                data["unit_type_b"] = version_regs[4]

            # ========== BULK READ 8: BLDC motor (333-335) - 3 registers ==========
            bldc_regs = await hass.async_add_executor_job(
                client.read_holding_registers_bulk, REG_BLDC_POWER, 3, 1, slave_id
            )
            if bldc_regs and len(bldc_regs) == 3:
                data["bldc_power"] = bldc_regs[0]  # 333 (W, 0.1)
                data["bldc_var"] = int(bldc_regs[1] * 10) if bldc_regs[1] is not None else None  # 334 (INT)
                data["bldc_current"] = bldc_regs[2]  # 335 (A, 0.1)

            # ========== BULK READ 9: SG Ready (355-363) - 9 registers ==========
            sg_regs = await hass.async_add_executor_job(
                client.read_holding_registers_bulk, REG_SG_MODE, 9, 0, slave_id
            )
            if sg_regs and len(sg_regs) == 9:
                data["sg_mode"] = sg_regs[0]  # 355 (INT)
                data["sg_mode_change_holdtime"] = sg_regs[1]  # 356 (INT)
                # SG temperatures and diffs (0.1 precision)
                data["sg_mode_w_tank_setp"] = float(sg_regs[2] / 10) if sg_regs[2] is not None else None  # 357
                data["sg_cool_setp_diff_1"] = float(sg_regs[3] / 10) if sg_regs[3] is not None else None  # 358
                data["sg_heat_setp_diff_1"] = float(sg_regs[4] / 10) if sg_regs[4] is not None else None  # 359
                data["sg_w_tank_setp_diff_1"] = float(sg_regs[5] / 10) if sg_regs[5] is not None else None  # 360
                data["sg_cool_setp_diff_2"] = float(sg_regs[6] / 10) if sg_regs[6] is not None else None  # 361
                data["sg_heat_setp_diff_2"] = float(sg_regs[7] / 10) if sg_regs[7] is not None else None  # 362
                data["sg_w_tank_setp_diff_2"] = float(sg_regs[8] / 10) if sg_regs[8] is not None else None  # 363

            # ========== BULK READ 10: Working Hours (364-371) - 8 registers ==========
            # Note: These are UDINT (32-bit) so each value uses 2 registers
            work_hours_regs = await hass.async_add_executor_job(
                client.read_holding_registers_bulk, REG_WORKING_HOURS_PUMP, 8, 0, slave_id
            )
            if work_hours_regs and len(work_hours_regs) == 8:
                # Combine 2 registers into 32-bit values
                data["working_hours_pump"] = (work_hours_regs[0] << 16) | work_hours_regs[1] if work_hours_regs[0] is not None and work_hours_regs[1] is not None else None
                data["working_hours_comp"] = (work_hours_regs[2] << 16) | work_hours_regs[3] if work_hours_regs[2] is not None and work_hours_regs[3] is not None else None
                data["working_hours_fan"] = (work_hours_regs[4] << 16) | work_hours_regs[5] if work_hours_regs[4] is not None and work_hours_regs[5] is not None else None
                data["working_hours_3way"] = (work_hours_regs[6] << 16) | work_hours_regs[7] if work_hours_regs[6] is not None and work_hours_regs[7] is not None else None

            # ========== BULK READ 11: Water Flow and Unit Power (372-389) - 18 registers ==========
            power_regs = await hass.async_add_executor_job(
                client.read_holding_registers_bulk, REG_WATER_FLOW, 18, 0, slave_id
            )
            if power_regs and len(power_regs) == 18:
                # Water flow (372-373, 2 registers REAL)
                data["water_flow"] = ((power_regs[0] << 16) | power_regs[1]) / 10 if power_regs[0] is not None and power_regs[1] is not None else None
                # Phase voltages and currents (376-381, 0.1 precision)
                data["phase_voltage_a"] = float(power_regs[4] / 10) if power_regs[4] is not None else None  # 376
                data["phase_voltage_b"] = float(power_regs[5] / 10) if power_regs[5] is not None else None  # 377
                data["phase_voltage_c"] = float(power_regs[6] / 10) if power_regs[6] is not None else None  # 378
                data["phase_current_a"] = float(power_regs[7] / 10) if power_regs[7] is not None else None  # 379
                data["phase_current_b"] = float(power_regs[8] / 10) if power_regs[8] is not None else None  # 380
                data["phase_current_c"] = float(power_regs[9] / 10) if power_regs[9] is not None else None  # 381
                # Power_W (382-383, 2 registers)
                data["power_w"] = ((power_regs[10] << 16) | power_regs[11]) / 10 if power_regs[10] is not None and power_regs[11] is not None else None
                # Total power consumption (384-385, 2 registers)
                data["total_power_consumption"] = ((power_regs[12] << 16) | power_regs[13]) / 10 if power_regs[12] is not None and power_regs[13] is not None else None
                # Unit power (387-388, 2 registers)
                data["unit_power"] = ((power_regs[15] << 16) | power_regs[16]) / 10 if power_regs[15] is not None and power_regs[16] is not None else None
                # Unit COP (389, 0.1 precision)
                data["unit_cop"] = float(power_regs[17] / 10) if power_regs[17] is not None else None

            # ========== BULK READ 12: Power consumption records (401-413) - 14 registers ==========
            # Note: Each record is 2 registers (REAL)
            record_regs = await hass.async_add_executor_job(
                client.read_holding_registers_bulk, REG_RECORD_POWER_1, 14, 0, slave_id
            )
            if record_regs and len(record_regs) == 14:
                data["record_power_1"] = ((record_regs[0] << 16) | record_regs[1]) / 10 if record_regs[0] is not None and record_regs[1] is not None else None
                data["record_power_2"] = ((record_regs[2] << 16) | record_regs[3]) / 10 if record_regs[2] is not None and record_regs[3] is not None else None
                data["record_power_3"] = ((record_regs[4] << 16) | record_regs[5]) / 10 if record_regs[4] is not None and record_regs[5] is not None else None
                data["record_power_4"] = ((record_regs[6] << 16) | record_regs[7]) / 10 if record_regs[6] is not None and record_regs[7] is not None else None
                data["record_power_5"] = ((record_regs[8] << 16) | record_regs[9]) / 10 if record_regs[8] is not None and record_regs[9] is not None else None
                data["record_power_6"] = ((record_regs[10] << 16) | record_regs[11]) / 10 if record_regs[10] is not None and record_regs[11] is not None else None
                data["record_power_7"] = ((record_regs[12] << 16) | record_regs[13]) / 10 if record_regs[12] is not None and record_regs[13] is not None else None

            # ========== BULK READ 13: Anti-legionella (471-477) - 7 registers ==========
            antileg_regs = await hass.async_add_executor_job(
                client.read_holding_registers_bulk, REG_ANTILEG_TEMP_SETP, 7, 0, slave_id
            )
            if antileg_regs and len(antileg_regs) == 7:
                # Temperature setpoint (471-472, 2 registers REAL)
                data["antileg_temp_setp"] = ((antileg_regs[0] << 16) | antileg_regs[1]) / 10 if antileg_regs[0] is not None and antileg_regs[1] is not None else None
                # Weekday (473)
                data["antileg_weekday"] = antileg_regs[2]
                # Start/End times (474-477)
                start_hr = antileg_regs[3]
                start_min = antileg_regs[4]
                if start_hr is not None and start_min is not None:
                    data["antileg_time_start"] = f"{int(start_hr):02d}:{int(start_min):02d}"
                else:
                    data["antileg_time_start"] = None

                end_hr = antileg_regs[5]
                end_min = antileg_regs[6]
                if end_hr is not None and end_min is not None:
                    data["antileg_time_end"] = f"{int(end_hr):02d}:{int(end_min):02d}"
                else:
                    data["antileg_time_end"] = None

            # ========== READ DISCRETE INPUTS (status - read only) ==========
            # These must be read individually
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

            # ========== READ ALL ALARMS (discrete inputs 13-188) ==========
            # Read alarms in bulk - 176 discrete inputs
            for alarm_reg in range(13, 189):
                data[f"alarm_{alarm_reg}"] = await hass.async_add_executor_job(
                    client.read_discrete_input, alarm_reg, slave_id
                )

            _LOGGER.debug("Successfully read all data via bulk operations")
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
