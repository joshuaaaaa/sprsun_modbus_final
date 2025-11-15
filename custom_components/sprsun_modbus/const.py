"""Constants for SPRSUN Heat Pump Modbus integration."""

DOMAIN = "sprsun_modbus"

# Config options
CONF_MODBUS_TYPE = "modbus_type"
CONF_MODBUS_SERIAL = "serial"
CONF_MODBUS_TCP = "tcp"
CONF_MODBUS_UDP = "udp"
CONF_SERIAL_PORT = "serial_port"
CONF_BAUDRATE = "baudrate"
CONF_SLAVE_ID = "slave_id"
CONF_REGISTER_OFFSET = "register_offset"  # NEW: Pro zařízení s offsetem (např. +2000)

# Default values
DEFAULT_PORT = "/dev/ttyUSB0"
DEFAULT_BAUDRATE = 19200
DEFAULT_SLAVE_ID = 1
DEFAULT_TCP_PORT = 4196
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_REGISTER_OFFSET = 0  # NEW: Standardně bez offsetu

# ============================================================================
# HOLDING REGISTERS (40001+)
# ============================================================================

# Basic control (40001-40020)
REG_WORK_MODE = 0  # 40001 - Mode SetP: 0=cooling, 1=heating, 2=hot water, 3=hot water+cooling, 4=hot water+heating (INT)
REG_HEATING_SETPOINT = 1  # 40002 - Heat SetP (REAL, 0.1)
REG_COOLING_SETPOINT = 2  # 40003 - Cool SetP (REAL, 0.1)
REG_HOTWATER_SETPOINT = 3  # 40004 - Hotwater SetP (REAL, 0.1)
REG_HW_START_DIFF = 4  # 40005 - hotwater_start_diff: 1.0~15.0 (REAL, 0.1)
REG_HW_STOP_DIFF = 5  # 40006 - hotwater_stop_diff: 0.0~5.0 (REAL, 0.1)
REG_CH_START_DIFF = 6  # 40007 - heat/cool start_Diff: 1.0~15.0 (REAL, 0.1)
REG_CH_STOP_DIFF = 7  # 40008 - heat/cool stop_Diff: 0.0~5.0 (REAL, 0.1)
REG_PUMP_START_INTERVAL = 8  # 40009 - Pump Start Interval: 0-30 minutes (UINT)
# REG 9-10 Reserved
REG_PUMP_MODE = 11  # 40012 - Pump mode: 0=Normal, 1=Demand, 2=Interval, 3=Always (INT)
REG_FAN_MODE = 12  # 40013 - Fan mode: 0=Daytime, 1=Night, 2=ECO mode, 3=Pressure (INT)
REG_COMP_DELAY = 13  # 40014 - E/H comp.delay: 0-999 (UINT)
REG_EXT_TEMP_SETP = 14  # 40015 - Ext.temp.setp.: -30.0~20.0 (REAL, 0.1)
# REG 15-19 Reserved

# Temperature and Pressure sensors (40189-40213)
REG_INLET_TEMP = 188  # 40189 - B1: Inlet temperature (REAL, 0.1)
REG_OUTLET_TEMP = 189  # 40190 - B2: Outlet temperature (REAL, 0.1)
REG_AMBIENT_TEMP = 190  # 40191 - B3: Ambient temperature (REAL, 0.1)
REG_DISCHARGE_TEMP = 191  # 40192 - B4: Discharge gas temperature (REAL, 0.1)
REG_SUCTION_TEMP = 192  # 40193 - B5: Suction gas temperature (REAL, 0.1)
REG_DISCHARGE_PRESS = 193  # 40194 - B6: Discharge pressure (REAL, 0.1)
REG_SUCTION_PRESS = 194  # 40195 - B7: Suction pressure (REAL, 0.1)
REG_HOTWATER_TEMP = 195  # 40196 - B8: Hot water temperature (REAL, 0.1)
REG_COIL_TEMP = 196  # 40197 - B9: Coil temperature (REAL, 0.1)
REG_FAN_OUTPUT = 197  # 40198 - Y1: Fan output (REAL, 0.1)
REG_PUMP_OUTPUT = 198  # 40199 - Y3: Pump output (REAL, 0.1)
REG_DC_FAN1_OUTPUT = 199  # 40200 - DC Fan 1 Output (REAL, 0.1)
REG_DC_FAN1_FEEDBACK = 200  # 40201 - DC Fan 1 Feedback
REG_DC_FAN2_OUTPUT = 201  # 40202 - DC Fan 2 Output (REAL, 0.1)
REG_DC_FAN2_FEEDBACK = 202  # 40203 - DC Fan 2 Feedback
REG_REQUIRED_CAP = 203  # 40204 - Required capacity (REAL, 0.1)
REG_ACTUAL_CAP = 204  # 40205 - Actual capacity (REAL, 0.1)
REG_ACTUAL_SPEED = 205  # 40206 - Actual speed
# REG 206 Reserved
REG_EEV_OPENING = 207  # 40208 - EEV opening
# REG 208 Reserved
REG_COMP_STATUS = 209  # 40210 - Compressor status
REG_COMP_PROTECTION = 210  # 40211 - Compressor protection
REG_SUCTION_SH = 211  # 40212 - Suction superheat (REAL, 0.1)
# REG 212 Reserved

# Unit run mode (40216)
REG_UNIT_RUN_MODE = 215  # 40216 - unit run mode: 0=Cooling, 1=Heating, 2=DHW (INT)

# Status (40218)
REG_STATUS = 217  # 40218 - Unit status

# Time setting (40183-40188)
REG_YEAR = 182  # 40183 - Year: 0~99 (UINT)
REG_MONTH = 183  # 40184 - Month: 0~12 (UINT)
REG_DAY = 184  # 40185 - Day: 0~31 (UINT)
REG_HOUR = 185  # 40186 - Hour: 0~23 (UINT)
REG_MINUTE = 186  # 40187 - Minute: 0~59 (UINT)
REG_WEEK = 187  # 40188 - Week: 1~7 (UINT)

# Timing on/off settings - Timezone1 (40219-40246)
# Note: These were incorrectly labeled as "EME" registers in previous version
# According to manufacturer table, these are Timezone1 Mon-Sun ON/OFF hours and minutes
REG_TZ1_MON_ON_HOUR = 218  # 40219 - Timezone1 Mon. ON: hour (0-23)
REG_TZ1_MON_ON_MIN = 219  # 40220 - Timezone1 Mon. ON: minute (0-59)
REG_TZ1_MON_OFF_HOUR = 220  # 40221 - Timezone1 Mon. OFF: hour (0-23)
REG_TZ1_MON_OFF_MIN = 221  # 40222 - Timezone1 Mon. OFF: minute (0-59)
REG_TZ1_TUE_ON_HOUR = 222  # 40223 - Timezone1 Tue. ON: hour (0-23)
REG_TZ1_TUE_ON_MIN = 223  # 40224 - Timezone1 Tue. ON: minute (0-59)
REG_TZ1_TUE_OFF_HOUR = 224  # 40225 - Timezone1 Tue. OFF: hour (0-23)
REG_TZ1_TUE_OFF_MIN = 225  # 40226 - Timezone1 Tue. OFF: minute (0-59)
REG_TZ1_WED_ON_HOUR = 226  # 40227 - Timezone1 Wed. ON: hour (0-23)
REG_TZ1_WED_ON_MIN = 227  # 40228 - Timezone1 Wed. ON: minute (0-59)
REG_TZ1_WED_OFF_HOUR = 228  # 40229 - Timezone1 Wed. OFF: hour (0-23)
REG_TZ1_WED_OFF_MIN = 229  # 40230 - Timezone1 Wed. OFF: minute (0-59)
REG_TZ1_THU_ON_HOUR = 230  # 40231 - Timezone1 Thu. ON: hour (0-23)
REG_TZ1_THU_ON_MIN = 231  # 40232 - Timezone1 Thu. ON: minute (0-59)
REG_TZ1_THU_OFF_HOUR = 232  # 40233 - Timezone1 Thu. OFF: hour (0-23)
REG_TZ1_THU_OFF_MIN = 233  # 40234 - Timezone1 Thu. OFF: minute (0-59)
REG_TZ1_FRI_ON_HOUR = 234  # 40235 - Timezone1 Fri. ON: hour (0-23)
REG_TZ1_FRI_ON_MIN = 235  # 40236 - Timezone1 Fri. ON: minute (0-59)
REG_TZ1_FRI_OFF_HOUR = 236  # 40237 - Timezone1 Fri. OFF: hour (0-23)
REG_TZ1_FRI_OFF_MIN = 237  # 40238 - Timezone1 Fri. OFF: minute (0-59)
REG_TZ1_SAT_ON_HOUR = 238  # 40239 - Timezone1 Sat. ON: hour (0-23)
REG_TZ1_SAT_ON_MIN = 239  # 40240 - Timezone1 Sat. ON: minute (0-59)
REG_TZ1_SAT_OFF_HOUR = 240  # 40241 - Timezone1 Sat. OFF: hour (0-23)
REG_TZ1_SAT_OFF_MIN = 241  # 40242 - Timezone1 Sat. OFF: minute (0-59)
REG_TZ1_SUN_ON_HOUR = 242  # 40243 - Timezone1 Sun. ON: hour (0-23)
REG_TZ1_SUN_ON_MIN = 243  # 40244 - Timezone1 Sun. ON: minute (0-59)
REG_TZ1_SUN_OFF_HOUR = 244  # 40245 - Timezone1 Sun. OFF: hour (0-23)
REG_TZ1_SUN_OFF_MIN = 245  # 40246 - Timezone1 Sun. OFF: minute (0-59)

# Time zone temperature settings (40247-40262)
REG_TZ_TEMP_HR1 = 246  # 40247 - TimezoneMng.TempHr1 (0-23)
REG_TZ_TEMP_MIN1 = 247  # 40248 - TimezoneMng.TempMin1 (0-59)
REG_TZ_S_SET_TEMP1 = 248  # 40249 - TimezoneMng.S_Set_Temp1 (-99.0~99.0 REAL)
REG_TZ_W_SET_TEMP1 = 249  # 40250 - TimezoneMng.W_Set_Temp1 (-99.0~99.0 REAL)
REG_TZ_TEMP_HR2 = 250  # 40251 - TimezoneMng.TempHr2 (0-23)
REG_TZ_TEMP_MIN2 = 251  # 40252 - TimezoneMng.TempMin2 (0-59)
REG_TZ_S_SET_TEMP2 = 252  # 40253 - TimezoneMng.S_Set_Temp2 (-99.0~99.0 REAL)
REG_TZ_W_SET_TEMP2 = 253  # 40254 - TimezoneMng.W_Set_Temp2 (-99.0~99.0 REAL)
REG_TZ_TEMP_HR3 = 254  # 40255 - TimezoneMng.TempHr3 (0-23)
REG_TZ_TEMP_MIN3 = 255  # 40256 - TimezoneMng.TempMin3 (0-59)
REG_TZ_S_SET_TEMP3 = 256  # 40257 - TimezoneMng.S_Set_Temp3 (-99.0~99.0 REAL)
REG_TZ_W_SET_TEMP3 = 257  # 40258 - TimezoneMng.W_Set_Temp3 (-99.0~99.0 REAL)
REG_TZ_TEMP_HR4 = 258  # 40259 - TimezoneMng.TempHr4 (0-23)
REG_TZ_TEMP_MIN4 = 259  # 40260 - TimezoneMng.TempMin4 (0-59)
REG_TZ_S_SET_TEMP4 = 260  # 40261 - TimezoneMng.S_Set_Temp4 (-99.0~99.0 REAL)
REG_TZ_W_SET_TEMP4 = 261  # 40262 - TimezoneMng.W_Set_Temp4 (-99.0~99.0 REAL)

# Engineering parameters
REG_HEATER_TYPE = 323  # 40324 - Heater type: 0=disable, 1=hotwater, 2=heating, 3=all, 4=independent (INT)

# Version and Unit Type (40326-40330)
REG_VERSION_X = 325  # 40326 - GeneralMng.CurrVer.X (INT)
REG_VERSION_Y = 326  # 40327 - GeneralMng.CurrVer.Y (INT)
REG_VERSION_Z = 327  # 40328 - GeneralMng.CurrVer.Z (INT)
REG_UNIT_TYPE_A = 328  # 40329 - GeneralMng.UnitType_A (INT)
REG_UNIT_TYPE_B = 329  # 40330 - GeneralMng.UnitType_B (INT)

# BLDC Motor (40334-40336)
REG_BLDC_POWER = 333  # 40334 - BLDC_POwer (W) (REAL, 0.1)
REG_BLDC_VAR = 334  # 40335 - BLDC_Var (INT)
REG_BLDC_CURRENT = 335  # 40336 - BLDC_Curret (A) (REAL, 0.1)

# Working Hours (40365-40371) - All UDINT (2 registers each!)
REG_WORKING_HOURS_PUMP = 364  # 40365-40366 - WorkingHours.Pump (UDINT, 2 registers)
REG_WORKING_HOURS_COMP = 366  # 40367-40368 - WorkingHours.Comp (UDINT, 2 registers)
REG_WORKING_HOURS_FAN = 368  # 40369-40370 - WorkingHours.Fan (UDINT, 2 registers)
REG_WORKING_HOURS_3WAY = 370  # 40371-40372 - WorkingHours.Three way valve (UDINT, 2 registers)

# Water Flow and Power (40373-40390)
REG_WATER_FLOW = 372  # 40373-40374 - Water Flow Value L/h (REAL, 2 registers)
REG_UNIT_POWER = 387  # 40388-40389 - Unit Power W (REAL, 2 registers)
REG_UNIT_COP = 389  # 40390 - Unit_COP (REAL, 0.1)

# SG Ready (40356-40364)
REG_SG_MODE = 355  # 40356 - SG_Mode: 0=NORMAL, 1=SG-, 2=SG+, 3=SG++ (INT)
REG_SG_MODE_CHANGE_HOLDTIME = 356  # 40357 - SG_Mode Change_HoldTime: 0~600s (INT)
REG_SG_MODE_W_TANK_SETP = 357  # 40358 - SG_Mode_W_Tank SetP: 56.0~70.0°C (REAL)
REG_SG_COOL_SETP_DIFF_1 = 358  # 40359 - SG_CoolSetP_Diff_1: 0.0~10.0°C (REAL)
REG_SG_HEAT_SETP_DIFF_1 = 359  # 40360 - SG_HeatSetP_Diff_1: 0.0~10.0°C (REAL)
REG_SG_W_TANK_SETP_DIFF_1 = 360  # 40361 - SG_W_TankSetP_Diff_1: 0.0~10.0°C (REAL)
REG_SG_COOL_SETP_DIFF_2 = 361  # 40362 - SG_CoolSetP_Diff_2: 0.0~10.0°C (REAL)
REG_SG_HEAT_SETP_DIFF_2 = 362  # 40363 - SG_HeatSetP_Diff_2: 0.0~10.0°C (REAL)
REG_SG_W_TANK_SETP_DIFF_2 = 363  # 40364 - SG_W_TankSetP_Diff_2: 0.0~10.0°C (REAL)

# Electric Meter (40377-40415)
REG_PHASE_VOLTAGE_A = 376  # 40377 - PhaseVoltage_A (V, REAL)
REG_PHASE_VOLTAGE_B = 377  # 40378 - PhaseVoltage_B (V, REAL)
REG_PHASE_VOLTAGE_C = 378  # 40379 - PhaseVoltage_C (V, REAL)
REG_PHASE_CURRENT_A = 379  # 40380 - PhaseCurrent_A (A, REAL)
REG_PHASE_CURRENT_B = 380  # 40381 - PhaseCurrent_B (A, REAL)
REG_PHASE_CURRENT_C = 381  # 40382 - PhaseCurrent_C (A, REAL)
REG_POWER_W = 382  # 40383-40384 - Power_W (W, REAL, 2 registers)
REG_TOTAL_POWER_CONSUMPTION = 384  # 40385-40386 - Total power consumption (Kw.h, REAL, 2 registers)
REG_RECORD_POWER_1 = 401  # 40402-40403 - Record_PowerConsumption[1] (Kw.h, REAL, 2 registers)
REG_RECORD_POWER_2 = 403  # 40404-40405 - Record_PowerConsumption[2] (Kw.h, REAL, 2 registers)
REG_RECORD_POWER_3 = 405  # 40406-40407 - Record_PowerConsumption[3] (Kw.h, REAL, 2 registers)
REG_RECORD_POWER_4 = 407  # 40408-40409 - Record_PowerConsumption[4] (Kw.h, REAL, 2 registers)
REG_RECORD_POWER_5 = 409  # 40410-40411 - Record_PowerConsumption[5] (Kw.h, REAL, 2 registers)
REG_RECORD_POWER_6 = 411  # 40412-40413 - Record_PowerConsumption[6] (Kw.h, REAL, 2 registers)
REG_RECORD_POWER_7 = 413  # 40414-40415 - Record_PowerConsumption[7] (Kw.h, REAL, 2 registers)

# Timing on/off settings - Timezone2 (40433-40460)
REG_TZ2_MON_ON_HOUR = 432  # 40433 - Timezone2 Mon. ON: hour (0-23)
REG_TZ2_MON_ON_MIN = 433  # 40434 - Timezone2 Mon. ON: minute (0-59)
REG_TZ2_MON_OFF_HOUR = 434  # 40435 - Timezone2 Mon. OFF: hour (0-23)
REG_TZ2_MON_OFF_MIN = 435  # 40436 - Timezone2 Mon. OFF: minute (0-59)
REG_TZ2_TUE_ON_HOUR = 436  # 40437 - Timezone2 Tue. ON: hour (0-23)
REG_TZ2_TUE_ON_MIN = 437  # 40438 - Timezone2 Tue. ON: minute (0-59)
REG_TZ2_TUE_OFF_HOUR = 438  # 40439 - Timezone2 Tue. OFF: hour (0-23)
REG_TZ2_TUE_OFF_MIN = 439  # 40440 - Timezone2 Tue. OFF: minute (0-59)
REG_TZ2_WED_ON_HOUR = 440  # 40441 - Timezone2 Wed. ON: hour (0-23)
REG_TZ2_WED_ON_MIN = 441  # 40442 - Timezone2 Wed. ON: minute (0-59)
REG_TZ2_WED_OFF_HOUR = 442  # 40443 - Timezone2 Wed. OFF: hour (0-23)
REG_TZ2_WED_OFF_MIN = 443  # 40444 - Timezone2 Wed. OFF: minute (0-59)
REG_TZ2_THU_ON_HOUR = 444  # 40445 - Timezone2 Thu. ON: hour (0-23)
REG_TZ2_THU_ON_MIN = 445  # 40446 - Timezone2 Thu. ON: minute (0-59)
REG_TZ2_THU_OFF_HOUR = 446  # 40447 - Timezone2 Thu. OFF: hour (0-23)
REG_TZ2_THU_OFF_MIN = 447  # 40448 - Timezone2 Thu. OFF: minute (0-59)
REG_TZ2_FRI_ON_HOUR = 448  # 40449 - Timezone2 Fri. ON: hour (0-23)
REG_TZ2_FRI_ON_MIN = 449  # 40450 - Timezone2 Fri. ON: minute (0-59)
REG_TZ2_FRI_OFF_HOUR = 450  # 40451 - Timezone2 Fri. OFF: hour (0-23)
REG_TZ2_FRI_OFF_MIN = 451  # 40452 - Timezone2 Fri. OFF: minute (0-59)
REG_TZ2_SAT_ON_HOUR = 452  # 40453 - Timezone2 Sat. ON: hour (0-23)
REG_TZ2_SAT_ON_MIN = 453  # 40454 - Timezone2 Sat. ON: minute (0-59)
REG_TZ2_SAT_OFF_HOUR = 454  # 40455 - Timezone2 Sat. OFF: hour (0-23)
REG_TZ2_SAT_OFF_MIN = 455  # 40456 - Timezone2 Sat. OFF: minute (0-59)
REG_TZ2_SUN_ON_HOUR = 456  # 40457 - Timezone2 Sun. ON: hour (0-23)
REG_TZ2_SUN_ON_MIN = 457  # 40458 - Timezone2 Sun. ON: minute (0-59)
REG_TZ2_SUN_OFF_HOUR = 458  # 40459 - Timezone2 Sun. OFF: hour (0-23)
REG_TZ2_SUN_OFF_MIN = 459  # 40460 - Timezone2 Sun. OFF: minute (0-59)

# Anti-legionella (40472-40478)
REG_ANTILEG_TEMP_SETP = 471  # 40472-40473 - Anti-legionella temp.setp.: 30-70°C (REAL, 2 registers)
REG_ANTILEG_WEEKDAY = 473  # 40474 - Weekday of running antileg.: 1~7 (UINT)
REG_ANTILEG_TIME_START_HR = 474  # 40475 - Timeband start - hours: 0-23 (UINT)
REG_ANTILEG_TIME_START_MIN = 475  # 40476 - Timeband start - minutes: 0-59 (UINT)
REG_ANTILEG_TIME_END_HR = 476  # 40477 - Timeband end - hours: 0-23 (UINT)
REG_ANTILEG_TIME_END_MIN = 477  # 40478 - Timeband end - minutes: 0-59 (UINT)

# ============================================================================
# COILS (00001+)
# ============================================================================
# NOTE: According to manufacturer's table, there is NO coil for Unit On/Off control
# Unit is controlled by setting Mode setP register (40001) to desired mode
# Unit On/OFF status is READ-ONLY via discrete input 10001

# Timezone coils
COIL_TIMEZONE_ENABLE = 38  # 00039 - timezone on/off enable
COIL_TIMEZONE_SETP_ENABLE = 39  # 00040 - timezone setpoint enable
COIL_SAVE_TIME = 43  # 00044 - save time

# Manual defrosting
COIL_MANUAL_DEFROST = 105  # 00106 - Manual defrosting: 0=disable, 1=enable

# Anti-legionella
COIL_ANTILEG_FUNCTION = 109  # 00110 - Anti-legionella function: 0=disable, 1=enable

# SG Ready
COIL_SG_FUNCTION = 63  # 00064 - En_SG_Function: 0=disable, 1=enable
COIL_SG_HOTWATER_HEATER = 64  # 00065 - En_SG_HotwaterHeater: 0=disable, 1=enable
COIL_SG_HEATER_PIPE_OR_TANK = 65  # 00066 - Hotwater Heater In Pipe or water tank: 0=water tank, 1=PIPE

# Electric Meter
COIL_ELECTRIC_METER_ENABLE = 67  # 00068 - Enable_ElectricMeter: 0=disable, 1=enable
COIL_ELECTRIC_METER_RESET = 68  # 00069 - ElectricMeter_Reset

# ============================================================================
# DISCRETE INPUTS (10001+)
# ============================================================================
DISCRETE_UNIT_ON = 0  # 10001 - Unit on/off status (READ-ONLY)
DISCRETE_FLOW_SWITCH = 1  # 10002 - Flow switch
# DISCRETE 2 Reserved (10003)
DISCRETE_AC_LINKAGE = 3  # 10004 - A/C linkage switch
DISCRETE_SG_SIGNAL = 4  # 10005 - SG_Signal
DISCRETE_DOUT_VAL_1 = 5  # 10006 - Outputs.DoutVal_1
DISCRETE_4WAY_VALVE = 7  # 10008 - Four way valve On/OFF status
DISCRETE_PUMP = 8  # 10009 - Pump On/OFF status
DISCRETE_3WAY_VALVE = 9  # 10010 - Three way valve On/OFF status
DISCRETE_CRANK_HEATER = 10  # 10011 - Crank.heater On/OFF status
DISCRETE_CHASSIS_HEATER = 11  # 10012 - chassis heater On/OFF status
DISCRETE_DOUT_VAL_9 = 12  # 10013 - Outputs.DoutVal_9
DISCRETE_COMP_STATUS = 179  # 10180 - Comp On/OFF status
DISCRETE_FAN_STATUS = 180  # 10181 - Fan On/OFF status
DISCRETE_EVU_SIGNAL = 187  # 10188 - EVU_Signal

# Legacy aliases for backward compatibility (will be removed)
COIL_FLOW_SWITCH = DISCRETE_FLOW_SWITCH
COIL_AC_LINKAGE = DISCRETE_AC_LINKAGE
COIL_FAN_HIGH = DISCRETE_DOUT_VAL_1  # Note: These might not be the same!
COIL_FAN_LOW = 6  # 10007 - Not in manufacturer table
COIL_4WAY_VALVE = DISCRETE_4WAY_VALVE
COIL_PUMP = DISCRETE_PUMP
COIL_THREE_VALVE = DISCRETE_3WAY_VALVE
COIL_CRANK_HEATER = DISCRETE_CRANK_HEATER
COIL_CHASSIS_HEATER = DISCRETE_CHASSIS_HEATER
COIL_HEATER = DISCRETE_DOUT_VAL_9
COIL_PHASE_SWITCH = DISCRETE_SG_SIGNAL

# Alarm discrete inputs (10014+)
COIL_COOLING_LINKAGE = 181  # 10182 - Cooling linkage
COIL_HEATING_LINKAGE = 182  # 10183 - Heating linkage
COIL_TERMINAL_PUMP = 183  # 10184 - Terminal pump

# ============================================================================
# WORK MODES
# ============================================================================
WORK_MODE_COOLING = 0
WORK_MODE_HEATING = 1
WORK_MODE_HOT_WATER = 2
WORK_MODE_HW_COOLING = 3
WORK_MODE_HW_HEATING = 4

WORK_MODE_MAP = {
    WORK_MODE_COOLING: "Cooling",
    WORK_MODE_HEATING: "Heating",
    WORK_MODE_HOT_WATER: "Hot Water",
    WORK_MODE_HW_COOLING: "Hot Water + Cooling",
    WORK_MODE_HW_HEATING: "Hot Water + Heating"
}

# ============================================================================
# STATUS VALUES
# ============================================================================
STATUS_MAP = {
    0: "Not Ready",
    1: "Unit ON",
    2: "OFF by Alarm",
    3: "OFF by Timezone",
    4: "OFF by SuperV",
    5: "OFF by Linkage",
    6: "OFF by Keyboard",
    7: "Manual Mode",
    8: "Anti Freeze",
    9: "OFF by AC linkage",
    10: "OFF by Change"
}

# ============================================================================
# UNIT RUN MODE
# ============================================================================
UNIT_RUN_MODE_COOLING = 0
UNIT_RUN_MODE_HEATING = 1
UNIT_RUN_MODE_DHW = 2

UNIT_RUN_MODE_MAP = {
    UNIT_RUN_MODE_COOLING: "Cooling",
    UNIT_RUN_MODE_HEATING: "Heating",
    UNIT_RUN_MODE_DHW: "DHW"
}

# ============================================================================
# FAN MODES
# ============================================================================
FAN_MODE_DAYTIME = 0
FAN_MODE_NIGHT = 1
FAN_MODE_ECO = 2
FAN_MODE_PRESSURE = 3

FAN_MODE_MAP = {
    FAN_MODE_DAYTIME: "Daytime",
    FAN_MODE_NIGHT: "Night",
    FAN_MODE_ECO: "ECO Mode",
    FAN_MODE_PRESSURE: "Pressure"
}

# ============================================================================
# HEATER TYPE
# ============================================================================
HEATER_TYPE_DISABLE = 0
HEATER_TYPE_HOTWATER = 1
HEATER_TYPE_HEATING = 2
HEATER_TYPE_ALL = 3
HEATER_TYPE_INDEPENDENT = 4

HEATER_TYPE_MAP = {
    HEATER_TYPE_DISABLE: "Disable",
    HEATER_TYPE_HOTWATER: "Hot Water",
    HEATER_TYPE_HEATING: "Heating",
    HEATER_TYPE_ALL: "All",
    HEATER_TYPE_INDEPENDENT: "Independent"
}

# ============================================================================
# PUMP MODES
# ============================================================================
PUMP_MODE_NORMAL = 0
PUMP_MODE_DEMAND = 1
PUMP_MODE_INTERVAL = 2
PUMP_MODE_ALWAYS = 3

PUMP_MODE_MAP = {
    PUMP_MODE_NORMAL: "Normal",
    PUMP_MODE_DEMAND: "Demand",
    PUMP_MODE_INTERVAL: "Interval",
    PUMP_MODE_ALWAYS: "Always"
}

# ============================================================================
# COMPRESSOR STATUS
# ============================================================================
COMP_STATUS_OK = 0
COMP_STATUS_CONTROLLED = 1
COMP_STATUS_LIMITED = 2

COMP_STATUS_MAP = {
    COMP_STATUS_OK: "OK",
    COMP_STATUS_CONTROLLED: "Controlled",
    COMP_STATUS_LIMITED: "Limited"
}

# ============================================================================
# ALARM REGISTERS (Discrete Inputs 10014+)
# ============================================================================
ALARM_REGISTERS = {
    13: "AL001 Too many mem writings",
    14: "AL002 Retain mem write error",
    15: "AL003 Inlet probe error",
    16: "AL004 Outlet probe error",
    17: "AL005 Ambient probe error",
    18: "AL006 Condenser coil temp",
    19: "AL007 Water flow switch",
    20: "AL008 Phase sequ.prot.alarm",
    21: "AL009 Unit work hour warning",
    22: "AL010 Pump work hour warning",
    23: "AL011 Comp.work hour warning",
    24: "AL012 Cond.fan work hourWarn",
    25: "AL013 Low superheat - Vlv.A",
    26: "AL014 Low superheat - Vlv.B",
    27: "AL015 LOP - Vlv.A",
    28: "AL016 LOP - Vlv.B",
    29: "AL017 MOP - Vlv.A",
    30: "AL018 MOP - Vlv.B",
    31: "AL019 Motor error - Vlv.A",
    32: "AL020 Motor error - Vlv.B",
    33: "AL021 Low suct.temp. - Vlv.A",
    34: "AL022 Low suct.temp. - Vlv.B",
    35: "AL023 High condens.temp.EVD",
    36: "AL024 Probe S1 error EVD",
    37: "AL025 Probe S2 error EVD",
    38: "AL026 Probe S3 error EVD",
    39: "AL027 Probe S4 error EVD",
    40: "AL028 Battery discharge EVD",
    41: "AL029 EEPROM alarm EVD",
    42: "AL030 Incomplete closing EVD",
    43: "AL031 Emergency closing EVD",
    44: "AL032 FW not compatible EVD",
    45: "AL033 Config. error EVD",
    46: "AL034 EVD Driver offline",
    47: "AL035 BLDC: High startup DeltaP",
    48: "AL036 BLDC: Compressor shut off",
    49: "AL037 BLDC: Out of Envelope",
    50: "AL038 BLDC: Starting fail wait",
    51: "AL039 BLDC: Starting fail exceeded",
    52: "AL040 BLDC: Low delta pressure",
    53: "AL041 BLDC: High discarge gas temp",
    54: "AL042 Envelope: High compressor ratio",
    55: "AL043 Envelope: High discharge press",
    56: "AL044 Envelope: High current",
    57: "AL045 Envelope: High suction pressure",
    58: "AL046 Envelope: Low compressor ratio",
    59: "AL047 Envelope: Low pressure diff",
    60: "AL048 Envelope: Low discharge pressure",
    61: "AL049 Envelope: Low suction pressure",
    62: "AL050 Envelope: High discharge temp",
    63: "AL051 Power+: 01-Overcurrent",
    64: "AL052 Power+: 02-Motor overload",
    65: "AL053 Power+: 03-DCbus overvoltage",
    66: "AL054 Power+: 04-DCbus undervoltage",
    67: "AL055 Power+: 05-Drive overtemp",
    68: "AL056 Power+: 06-Drive undertemp",
    69: "AL057 Power+: 07-Overcurrent HW",
    70: "AL058 Power+: 08-Motor overtemp",
    71: "AL059 Power+: 09-IGBT module error",
    72: "AL060 Power+: 10-CPU error",
    73: "AL061 Power+: 11-Parameter default",
    74: "AL062 Power+: 12-DCbus ripple",
    75: "AL063 Power+: 13-Data comm. Fault",
    76: "AL064 Power+: 14-Thermistor fault",
    77: "AL065 Power+: 15-Autotuning fault",
    78: "AL066 Power+: 16-Drive disabled",
    79: "AL067 Power+: 17-Motor phase fault",
    80: "AL068 Power+: 18-Internal fan fault",
    81: "AL069 Power+: 19-Speed fault",
    82: "AL070 Power+: 20-PFC module error",
    83: "AL071 Power+: 21-PFC overvoltage",
    84: "AL072 Power+: 22-PFC undervoltage",
    85: "AL073 Power+: 23-STO DetectionError",
    86: "AL074 Power+: 24-STO DetectionError",
    87: "AL075 Power+: 25-Ground fault",
    88: "AL076 Power+: 26-Internal error 1",
    89: "AL077 Power+: 27-Internal error 2",
    90: "AL078 Power+: 28-Drive overload",
    91: "AL079 Power+: 29-uC safety fault",
    92: "AL080 Power+: 98-Unexpected restart",
    93: "AL081 Power+: 99-Unexpected stop",
    94: "AL082 Power+ safety: 01-Current meas.fault",
    95: "AL083 Power+ safety: 02-Current unbalanced",
    96: "AL084 Power+ safety: 03-Over current",
    97: "AL085 Power+ safety: 04-STO alarm",
    98: "AL086 Power+ safety: 05-STO hardware alarm",
    99: "AL087 Power+ safety: 06-PowerSupply missing",
    100: "AL088 Power+ safety: 07-HW fault cmd.buffer",
    101: "AL089 Power+ safety: 08-HW fault heater c.",
    102: "AL090 Power+ safety: 09-Data comm. Fault",
    103: "AL091 Power+ safety: 10-Compr. stall detect",
    104: "AL092 Power+ safety: 11-DCbus over current",
    105: "AL093 Power+ safety: 12-HWF DCbus current",
    106: "AL094 Power+ safety: 13-DCbus voltage",
    107: "AL095 Power+ safety: 14-HWF DCbus voltage",
    108: "AL096 Power+ safety: 15-Input voltage",
    109: "AL097 Power+ safety: 16-HWF input voltage",
    110: "AL098 Power+ safety: 17-DCbus power alarm",
    111: "AL099 Power+ safety: 18-HWF power mismatch",
    112: "AL100 Power+ safety: 19-NTC over temp",
    113: "AL101 Power+ safety: 20-NTC under temp",
    114: "AL102 Power+ safety: 21-NTC fault",
    115: "AL103 Power+ safety: 22-HWF sync fault",
    116: "AL104 Power+ safety: 23-Invalid parameter",
    117: "AL105 Power+ safety: 24-FW fault",
    118: "AL106 Power+ safety: 25-HW fault",
    119: "AL107 Power+ safety: 26-reserved",
    120: "AL108 Power+ safety: 27-reserved",
    121: "AL109 Power+ safety: 28-reserved",
    122: "AL110 Power+ safety: 29-reserved",
    123: "AL111 Power+ safety: 30-reserved",
    124: "AL112 Power+ safety: 31-reserved",
    125: "AL113 Power+ safety: 32-reserved",
    126: "AL114 Power+: Power+ offline",
    127: "AL115 EEV: Low superheat",
    128: "AL116 EEV: LOP",
    129: "AL117 EEV: MOP",
    130: "AL118 EEV: High condens.temp",
    131: "AL119 EEV: Low suction temp",
    132: "AL120 EEV: Motor error",
    133: "AL121 EEV: Self Tuning",
    134: "AL122 EEV: Emergency closing",
    135: "AL123 EEV: Temperature delta",
    136: "AL124 EEV: Pressure delta",
    137: "AL125 EEV: Param.range error",
    138: "AL126 EEV: ServicePosit% err",
    139: "AL127 EEV: ValveID pin error",
    140: "AL128 Low press alarm",
    141: "AL129 High press alarm",
    142: "AL130 Disc.temp.probe error",
    143: "AL131 Suct.temp.probe error",
    144: "AL132 Disc.press.probe error",
    145: "AL133 Suct.press.probe error",
    146: "AL134 Tank temp.probe error",
    147: "AL135 EVI SuctT.probe error",
    148: "AL136 EVI SuctP.probe error",
    149: "AL137 Flow switch alarm",
    150: "AL138 High temp. alarm",
    151: "AL139 Low temp. alarm",
    152: "AL140 Temp.delta alarm",
    153: "AL141 EVI: Param.range error",
    154: "AL142 EVI: Low superheat",
    155: "AL143 EVI: LOP",
    156: "AL144 EVI: MOP",
    157: "AL145 EVI: High condens.temp",
    158: "AL146 EVI: Low suction temp",
    159: "AL147 EVI: Motor error",
    160: "AL148 EVI: Self Tuning",
    161: "AL149 EVI: Emergency closing",
    162: "AL150 EVI: ServicePosit% err",
    163: "AL151 EVI: ValveID pin error",
    164: "AL152 Supply power error",
    165: "AL153 Fan1 fault",
    166: "AL154 Fan2 fault",
    167: "AL155 Fans Offline",
    168: "AL165 Slave1 Offline",
    169: "AL166 Master Offline",
    170: "AL167 Slave2 Offline",
    171: "AL168 Slave3 Offline",
    172: "AL169 Slave4 Offline",
    173: "AL170 Slave5 Offline",
    174: "AL171 Slave6 Offline",
    175: "AL172 Slave7 Offline",
    176: "AL173 Slave8 Offline",
    177: "AL174 Slave9 Offline",
    188: "AL177 Electric Meter Offline",
}

# ============================================================================
# SG READY MODES
# ============================================================================
SG_MODE_NORMAL = 0
SG_MODE_MINUS = 1
SG_MODE_PLUS = 2
SG_MODE_PLUS_PLUS = 3

SG_MODE_MAP = {
    SG_MODE_NORMAL: "Normal",
    SG_MODE_MINUS: "SG-",
    SG_MODE_PLUS: "SG+",
    SG_MODE_PLUS_PLUS: "SG++"
}

# ============================================================================
# WEEKDAY MAP
# ============================================================================
WEEKDAY_MAP = {
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
    7: "Sunday"
}
