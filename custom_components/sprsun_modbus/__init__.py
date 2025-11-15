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


def combine_32bit_registers(high: int, low: int) -> int | None:
    """Combine two 16-bit registers into 32-bit unsigned integer.
    
    Args:
        high: High 16-bit register value
        low: Low 16-bit register value
        
    Returns:
        32-bit unsigned integer or None if any value is None
    """
    if high is None or low is None:
        return None
    # Ensure values are unsigned 16-bit
    high = high & 0xFFFF
    low = low & 0xFFFF
    return (high << 16) | low


def registers_to_float32(high: int, low: int) -> float | None:
    """Convert two 16-bit registers to 32-bit float (IEEE 754).
    
    Args:
        high: High 16-bit register value
        low: Low 16-bit register value
        
    Returns:
        32-bit float or None if any value is None
    """
    if high is None or low is None:
        return None
    import struct
    # Ensure values are unsigned 16-bit
    high = high & 0xFFFF
    low = low & 0xFFFF
    # Combine into 32-bit integer (big-endian order)
    combined = (high << 16) | low
    # Convert to float using struct
    try:
        return struct.unpack('>f', struct.pack('>I', combined))[0]
    except:
        return None


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
                client.read_holding_registers_bulk, 0, 15, 0, slave_id, True  # raw=True
            )
            if control_regs and len(control_regs) == 15:
                # Helper functions
                def to_temp(val):
                    if val is None:
                        return None
                    if val > 32767:
                        val = val - 65536
                    return float(val / 10)
                
                def to_int(val):
                    if val is None:
                        return None
                    if val > 32767:
                        val = val - 65536
                    return int(val)
                
                data["work_mode"] = to_int(control_regs[0])  # 0 (INT)
                data["heating_setpoint"] = to_temp(control_regs[1])  # 1 (REAL 0.1)
                data["cooling_setpoint"] = to_temp(control_regs[2])  # 2 (REAL 0.1)
                data["hotwater_setpoint"] = to_temp(control_regs[3])  # 3 (REAL 0.1)
                data["hw_start_diff"] = to_temp(control_regs[4])  # 4 (REAL 0.1)
                data["hw_stop_diff"] = to_temp(control_regs[5])  # 5 (REAL 0.1)
                data["ch_start_diff"] = to_temp(control_regs[6])  # 6 (REAL 0.1)
                data["ch_stop_diff"] = to_temp(control_regs[7])  # 7 (REAL 0.1)
                # register 8 is pump_start_interval - not used in sensors
                # registers 9-10 are reserved
                data["pump_mode"] = to_int(control_regs[11])  # 11 (INT)
                data["fan_mode"] = to_int(control_regs[12])  # 12 (INT)
                data["comp_delay"] = to_int(control_regs[13])  # 13 (UINT)
                data["ext_temp_setp"] = to_temp(control_regs[14])  # 14 (REAL 0.1)

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
                client.read_holding_registers_bulk, REG_INLET_TEMP, 24, 0, slave_id, True  # raw=True
            )
            if sensors_regs and len(sensors_regs) == 24:
                # Helper function for signed conversion with 0.1 precision
                def to_temp(val):
                    if val is None:
                        return None
                    if val > 32767:
                        val = val - 65536
                    return float(val / 10)
                
                # Helper function for signed conversion without decimal (INT values)
                def to_int(val):
                    if val is None:
                        return None
                    if val > 32767:
                        val = val - 65536
                    return int(val)
                
                data["inlet_temp"] = to_temp(sensors_regs[0])  # 188
                data["outlet_temp"] = to_temp(sensors_regs[1])  # 189
                data["ambient_temp"] = to_temp(sensors_regs[2])  # 190
                data["discharge_temp"] = to_temp(sensors_regs[3])  # 191
                data["suction_temp"] = to_temp(sensors_regs[4])  # 192
                data["discharge_press"] = to_temp(sensors_regs[5])  # 193
                data["suction_press"] = to_temp(sensors_regs[6])  # 194
                data["hotwater_temp"] = to_temp(sensors_regs[7])  # 195
                data["coil_temp"] = to_temp(sensors_regs[8])  # 196
                data["fan_output"] = to_temp(sensors_regs[9])  # 197
                data["pump_output"] = to_temp(sensors_regs[10])  # 198
                data["dc_fan1_output"] = to_temp(sensors_regs[11])  # 199
                data["dc_fan1_feedback"] = to_int(sensors_regs[12])  # 200 (RPM - INT)
                data["dc_fan2_output"] = to_temp(sensors_regs[13])  # 201
                data["dc_fan2_feedback"] = to_int(sensors_regs[14])  # 202 (RPM - INT)
                data["required_cap"] = to_temp(sensors_regs[15])  # 203
                data["actual_cap"] = to_temp(sensors_regs[16])  # 204
                data["actual_speed"] = to_int(sensors_regs[17])  # 205 (RPM - INT)
                # 206 is reserved
                data["eev_opening"] = to_int(sensors_regs[19])  # 207 (INT)
                # 208 is reserved
                data["comp_status"] = to_int(sensors_regs[21])  # 209 (INT)
                data["comp_protection"] = to_int(sensors_regs[22])  # 210 (INT)
                data["suction_sh"] = to_temp(sensors_regs[23])  # 211

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
                client.read_holding_registers_bulk, REG_TZ_TEMP_HR1, 16, 0, slave_id, True  # raw=True
            )
            if tz_temp_regs and len(tz_temp_regs) == 16:
                # Helper functions
                def to_temp(val):
                    if val is None:
                        return None
                    if val > 32767:
                        val = val - 65536
                    return float(val / 10)
                
                def to_int(val):
                    if val is None:
                        return None
                    if val > 32767:
                        val = val - 65536
                    return int(val)
                
                # Time values (no decimal) and temp values (0.1 precision)
                data["tz_temp_hr1"] = to_int(tz_temp_regs[0])
                data["tz_temp_min1"] = to_int(tz_temp_regs[1])
                data["tz_s_set_temp1"] = to_temp(tz_temp_regs[2])
                data["tz_w_set_temp1"] = to_temp(tz_temp_regs[3])
                data["tz_temp_hr2"] = to_int(tz_temp_regs[4])
                data["tz_temp_min2"] = to_int(tz_temp_regs[5])
                data["tz_s_set_temp2"] = to_temp(tz_temp_regs[6])
                data["tz_w_set_temp2"] = to_temp(tz_temp_regs[7])
                data["tz_temp_hr3"] = to_int(tz_temp_regs[8])
                data["tz_temp_min3"] = to_int(tz_temp_regs[9])
                data["tz_s_set_temp3"] = to_temp(tz_temp_regs[10])
                data["tz_w_set_temp3"] = to_temp(tz_temp_regs[11])
                data["tz_temp_hr4"] = to_int(tz_temp_regs[12])
                data["tz_temp_min4"] = to_int(tz_temp_regs[13])
                data["tz_s_set_temp4"] = to_temp(tz_temp_regs[14])
                data["tz_w_set_temp4"] = to_temp(tz_temp_regs[15])

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
                client.read_holding_registers_bulk, REG_BLDC_POWER, 3, 0, slave_id, True  # raw=True
            )
            if bldc_regs and len(bldc_regs) == 3:
                # BLDC Power (W, 0.1 precision)
                bldc_power_raw = bldc_regs[0]
                if bldc_power_raw is not None:
                    if bldc_power_raw > 32767:
                        bldc_power_raw = bldc_power_raw - 65536
                    data["bldc_power"] = float(bldc_power_raw / 10)
                else:
                    data["bldc_power"] = None
                    
                # BLDC Var (INT - no decimal)
                bldc_var_raw = bldc_regs[1]
                if bldc_var_raw is not None:
                    if bldc_var_raw > 32767:
                        bldc_var_raw = bldc_var_raw - 65536
                    data["bldc_var"] = int(bldc_var_raw)
                else:
                    data["bldc_var"] = None
                    
                # BLDC Current (A, 0.1 precision)
                bldc_current_raw = bldc_regs[2]
                if bldc_current_raw is not None:
                    if bldc_current_raw > 32767:
                        bldc_current_raw = bldc_current_raw - 65536
                    data["bldc_current"] = float(bldc_current_raw / 10)
                else:
                    data["bldc_current"] = None

            # ========== BULK READ 9: SG Ready (355-363) - 9 registers ==========
            sg_regs = await hass.async_add_executor_job(
                client.read_holding_registers_bulk, REG_SG_MODE, 9, 0, slave_id, True  # raw=True
            )
            if sg_regs and len(sg_regs) == 9:
                # Helper functions
                def to_temp(val):
                    if val is None:
                        return None
                    if val > 32767:
                        val = val - 65536
                    return float(val / 10)
                
                def to_int(val):
                    if val is None:
                        return None
                    if val > 32767:
                        val = val - 65536
                    return int(val)
                
                data["sg_mode"] = to_int(sg_regs[0])  # 355 (INT)
                data["sg_mode_change_holdtime"] = to_int(sg_regs[1])  # 356 (INT)
                # SG temperatures and diffs (0.1 precision)
                data["sg_mode_w_tank_setp"] = to_temp(sg_regs[2])  # 357
                data["sg_cool_setp_diff_1"] = to_temp(sg_regs[3])  # 358
                data["sg_heat_setp_diff_1"] = to_temp(sg_regs[4])  # 359
                data["sg_w_tank_setp_diff_1"] = to_temp(sg_regs[5])  # 360
                data["sg_cool_setp_diff_2"] = to_temp(sg_regs[6])  # 361
                data["sg_heat_setp_diff_2"] = to_temp(sg_regs[7])  # 362
                data["sg_w_tank_setp_diff_2"] = to_temp(sg_regs[8])  # 363

            # ========== BULK READ 10: Working Hours (364-371) - 8 registers ==========
            # Note: These are UDINT (32-bit unsigned) so each value uses 2 registers
            work_hours_regs = await hass.async_add_executor_job(
                client.read_holding_registers_bulk, REG_WORKING_HOURS_PUMP, 8, 0, slave_id, True  # raw=True
            )
            if work_hours_regs and len(work_hours_regs) == 8:
                # Combine 2 registers into 32-bit unsigned values
                data["working_hours_pump"] = combine_32bit_registers(work_hours_regs[0], work_hours_regs[1])
                data["working_hours_comp"] = combine_32bit_registers(work_hours_regs[2], work_hours_regs[3])
                data["working_hours_fan"] = combine_32bit_registers(work_hours_regs[4], work_hours_regs[5])
                data["working_hours_3way"] = combine_32bit_registers(work_hours_regs[6], work_hours_regs[7])

            # ========== BULK READ 11: Water Flow and Unit Power (372-389) - 18 registers ==========
            power_regs = await hass.async_add_executor_job(
                client.read_holding_registers_bulk, REG_WATER_FLOW, 18, 0, slave_id, True  # raw=True
            )
            if power_regs and len(power_regs) == 18:
                # Water flow (372-373, 2 registers REAL/FLOAT32)
                water_flow_raw = registers_to_float32(power_regs[0], power_regs[1])
                data["water_flow"] = water_flow_raw if water_flow_raw is not None else None
                
                # Registers 374-375 are part of water flow or reserved
                
                # Phase voltages and currents (376-381, single register REAL with 0.1 precision)
                # Note: These need signed conversion
                def to_signed_16bit(val):
                    if val is None:
                        return None
                    if val > 32767:
                        val = val - 65536
                    return float(val / 10)
                
                data["phase_voltage_a"] = to_signed_16bit(power_regs[4])  # 376
                data["phase_voltage_b"] = to_signed_16bit(power_regs[5])  # 377
                data["phase_voltage_c"] = to_signed_16bit(power_regs[6])  # 378
                data["phase_current_a"] = to_signed_16bit(power_regs[7])  # 379
                data["phase_current_b"] = to_signed_16bit(power_regs[8])  # 380
                data["phase_current_c"] = to_signed_16bit(power_regs[9])  # 381
                
                # Power_W (382-383, 2 registers REAL/FLOAT32)
                power_w_raw = registers_to_float32(power_regs[10], power_regs[11])
                data["power_w"] = power_w_raw if power_w_raw is not None else None
                
                # Total power consumption (384-385, 2 registers REAL/FLOAT32)
                total_power_raw = registers_to_float32(power_regs[12], power_regs[13])
                data["total_power_consumption"] = total_power_raw if total_power_raw is not None else None
                
                # Register 386 might be part of total_power or reserved
                
                # Unit power (387-388, 2 registers REAL/FLOAT32)
                unit_power_raw = registers_to_float32(power_regs[15], power_regs[16])
                data["unit_power"] = unit_power_raw if unit_power_raw is not None else None
                
                # Unit COP (389, single register with 0.1 precision)
                data["unit_cop"] = to_signed_16bit(power_regs[17])

            # ========== BULK READ 12: Power consumption records (401-414) - 14 registers ==========
            # Note: Each record is 2 registers (REAL/FLOAT32)
            record_regs = await hass.async_add_executor_job(
                client.read_holding_registers_bulk, REG_RECORD_POWER_1, 14, 0, slave_id, True  # raw=True
            )
            if record_regs and len(record_regs) == 14:
                data["record_power_1"] = registers_to_float32(record_regs[0], record_regs[1])
                data["record_power_2"] = registers_to_float32(record_regs[2], record_regs[3])
                data["record_power_3"] = registers_to_float32(record_regs[4], record_regs[5])
                data["record_power_4"] = registers_to_float32(record_regs[6], record_regs[7])
                data["record_power_5"] = registers_to_float32(record_regs[8], record_regs[9])
                data["record_power_6"] = registers_to_float32(record_regs[10], record_regs[11])
                data["record_power_7"] = registers_to_float32(record_regs[12], record_regs[13])

            # ========== BULK READ 13: Anti-legionella (471-477) - 7 registers ==========
            antileg_regs = await hass.async_add_executor_job(
                client.read_holding_registers_bulk, REG_ANTILEG_TEMP_SETP, 7, 0, slave_id, True  # raw=True
            )
            if antileg_regs and len(antileg_regs) == 7:
                # Temperature setpoint (471-472, 2 registers REAL/FLOAT32)
                data["antileg_temp_setp"] = registers_to_float32(antileg_regs[0], antileg_regs[1])
                
                # Weekday (473) - needs signed conversion
                weekday_raw = antileg_regs[2]
                if weekday_raw is not None and weekday_raw > 32767:
                    weekday_raw = weekday_raw - 65536
                data["antileg_weekday"] = weekday_raw
                
                # Start/End times (474-477) - need signed conversion
                start_hr = antileg_regs[3]
                if start_hr is not None and start_hr > 32767:
                    start_hr = start_hr - 65536
                start_min = antileg_regs[4]
                if start_min is not None and start_min > 32767:
                    start_min = start_min - 65536
                    
                if start_hr is not None and start_min is not None:
                    data["antileg_time_start"] = f"{int(start_hr):02d}:{int(start_min):02d}"
                else:
                    data["antileg_time_start"] = None

                end_hr = antileg_regs[5]
                if end_hr is not None and end_hr > 32767:
                    end_hr = end_hr - 65536
                end_min = antileg_regs[6]
                if end_min is not None and end_min > 32767:
                    end_min = end_min - 65536
                    
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
