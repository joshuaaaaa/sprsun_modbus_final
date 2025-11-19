# Validace Modbus Registrů podle Tabulky

## Problém
Po včerejším update nefunguje `sensor.sprsun_unit_cop`

## Kontrola podle tabulky

### 1. Status Query - Hlavní senzory (REG 188-211)

| Senzor | Tabulka (add/modbus/byte/type) | Kód (const.py) | Mapování (__init__.py) | Status |
|--------|-------------------------------|----------------|----------------------|--------|
| Inlet Temp | 188/40189/1/REAL | REG_INLET_TEMP=188 | sensors_regs[0] @ 188 | ✓ OK |
| Outlet Temp | 189/40190/1/REAL | REG_OUTLET_TEMP=189 | sensors_regs[1] @ 189 | ✓ OK |
| Amb.Temp | 190/40191/1/REAL | REG_AMBIENT_TEMP=190 | sensors_regs[2] @ 190 | ✓ OK |
| Disch.gas Temp | 191/40192/1/REAL | REG_DISCHARGE_TEMP=191 | sensors_regs[3] @ 191 | ✓ OK |
| Suct.gas Temp | 192/40193/1/REAL | REG_SUCTION_TEMP=192 | sensors_regs[4] @ 192 | ✓ OK |
| Disch.press | 193/40194/1/REAL | REG_DISCHARGE_PRESS=193 | sensors_regs[5] @ 193 | ✓ OK |
| Suct.press | 194/40195/1/REAL | REG_SUCTION_PRESS=194 | sensors_regs[6] @ 194 | ✓ OK |
| hotwater temp | 195/40196/1/REAL | REG_HOTWATER_TEMP=195 | sensors_regs[7] @ 195 | ✓ OK |
| Coil Temp | 196/40197/1/REAL | REG_COIL_TEMP=196 | sensors_regs[8] @ 196 | ✓ OK |
| Fan output(%) | 197/40198/1/REAL | REG_FAN_OUTPUT=197 | sensors_regs[9] @ 197 | ✓ OK |
| Pump out(%) | 198/40199/1/REAL | REG_PUMP_OUTPUT=198 | sensors_regs[10] @ 198 | ✓ OK |
| Fan2 RPM | 200/40201/1/INT | REG_DC_FAN2_FEEDBACK=202 | sensors_regs[14] @ 202 | ❌ CHYBA! |
| Fan1 RPM | 202/40203/1/INT | REG_DC_FAN1_FEEDBACK=200 | sensors_regs[12] @ 200 | ❌ CHYBA! |
| COMP.RPM | 205/40206/1/REAL | REG_ACTUAL_SPEED=205 | sensors_regs[17] @ 205 | ✓ OK |
| EEV1 Steps | 207/40208/1/INT | REG_EEV_OPENING=207 | sensors_regs[19] @ 207 | ✓ OK |
| unit run mode | 215/40216/1/INT | REG_UNIT_RUN_MODE=215 | status_regs[0] @ 215 | ✓ OK |

**NALEZENA CHYBA #1**: Fan1 RPM a Fan2 RPM jsou prohozené!
- Tabulka: Fan2 RPM = reg 200, Fan1 RPM = reg 202
- Kód: DC_FAN1_FEEDBACK = reg 200, DC_FAN2_FEEDBACK = reg 202

### 2. BLDC Motor (REG 333-335)

| Senzor | Tabulka (add/modbus/byte/type) | Kód (const.py) | Mapování (__init__.py) | Status |
|--------|-------------------------------|----------------|----------------------|--------|
| BLDC_Power | 333/40334/1/real | REG_BLDC_POWER=333 | bldc_regs[0] @ 333 | ✓ OK |
| BLDC_Var | 334/40335/1/int | REG_BLDC_VAR=334 | bldc_regs[1] @ 334 | ✓ OK |
| BLDC_Current | 335/40336/1/real | REG_BLDC_CURRENT=335 | bldc_regs[2] @ 335 | ✓ OK |

### 3. Working Hours (REG 364-371) - UDINT (32-bit)

| Senzor | Tabulka (add/modbus/byte/type) | Kód (const.py) | Mapování (__init__.py) | Status |
|--------|-------------------------------|----------------|----------------------|--------|
| WorkingHours.Pump | 364/40365/2/UDINT | REG_WORKING_HOURS_PUMP=364 | work_hours_regs[0-1] @ 364-365 | ✓ OK |
| WorkingHours.Comp | 366/40367/2/UDINT | REG_WORKING_HOURS_COMP=366 | work_hours_regs[2-3] @ 366-367 | ✓ OK |
| WorkingHours.Fan | 368/40369/2/UDINT | REG_WORKING_HOURS_FAN=368 | work_hours_regs[4-5] @ 368-369 | ✓ OK |
| WorkingHours.3way | 370/40371/2/UDINT | REG_WORKING_HOURS_3WAY=370 | work_hours_regs[6-7] @ 370-371 | ✓ OK |

### 4. Water Flow and Unit Power (REG 372-390) **KRITICKÁ SEKCE**

| Senzor | Tabulka (add/modbus/byte/type) | Kód (const.py) | Mapování (__init__.py) | Status |
|--------|-------------------------------|----------------|----------------------|--------|
| Water Flow Value | 372/40373/2/real | REG_WATER_FLOW=372 | power_regs[0-1] @ 372-373 | ✓ OK |
| Unit Power | 387/40388/2/real | REG_UNIT_POWER=387 | power_regs[15-16] @ 387-388 | ✓ OK |
| **Unit_COP** | **389/40390/1/real** | **REG_UNIT_COP=389** | **power_regs[17] @ 389** | **❓ PROBLÉM!** |

**NALEZEN PROBLÉM #2**: Unit_COP
- Tabulka říká: byte=1, real (měl by být 1 registr s 0.1 precision)
- Aktuální kód čte: power_regs[17] jako signed 16-bit / 10
- **ALE**: Bulkové čtení čte pouze 18 registrů (372-389)
- **POKUD** je Unit_COP ve skutečnosti 32-bit float (byte=2), pak:
  - Potřebujeme registry 389-390 (2 registry)
  - Aktuální čtení končí na 389, takže chybí registr 390!

### 5. Electric Meter (REG 376-415)

| Senzor | Tabulka (add/modbus/byte/type) | Kód (const.py) | Mapování (__init__.py) | Status |
|--------|-------------------------------|----------------|----------------------|--------|
| PhaseVoltage_A | 376/40377/1/real | REG_PHASE_VOLTAGE_A=376 | power_regs[4] @ 376 | ✓ OK |
| PhaseVoltage_B | 377/40378/1/real | REG_PHASE_VOLTAGE_B=377 | power_regs[5] @ 377 | ✓ OK |
| PhaseVoltage_C | 378/40379/1/real | REG_PHASE_VOLTAGE_C=378 | power_regs[6] @ 378 | ✓ OK |
| PhaseCurrent_A | 379/40380/1/real | REG_PHASE_CURRENT_A=379 | power_regs[7] @ 379 | ✓ OK |
| PhaseCurrent_B | 380/40381/1/real | REG_PHASE_CURRENT_B=380 | power_regs[8] @ 380 | ✓ OK |
| PhaseCurrent_C | 381/40382/1/real | REG_PHASE_CURRENT_C=381 | power_regs[9] @ 381 | ✓ OK |
| Power_W | 382/40383/2/real | REG_POWER_W=382 | power_regs[10-11] @ 382-383 | ✓ OK |
| Total power consumption | 384/40385/2/real | REG_TOTAL_POWER_CONSUMPTION=384 | power_regs[12-13] @ 384-385 | ✓ OK |
| Record_PowerConsumption[1] | 401/40402/2/REAL | REG_RECORD_POWER_1=401 | record_regs[0-1] @ 401-402 | ✓ OK |

## SOUHRN NALEZENÝCH CHYB:

1. **Fan RPM Registry jsou prohozené** (const.py řádky 57-59):
   - Fan1 RPM by měl být na reg 202 (ne 200)
   - Fan2 RPM by měl být na reg 200 (ne 202)

2. **Unit_COP možná potřebuje 2 registry** (__init__.py řádek 330-371):
   - Pokud je Unit_COP ve skutečnosti 32-bit float (ne 16-bit scaled):
     - Bulkové čtení musí být 19 registrů (372-390) místo 18
     - Unit_COP musí být čten jako float32 z power_regs[17-18]
   - NEBO dokumentace výrobce je chybná a byte=1 je správně

## DOPORUČENÉ OPRAVY:

### Oprava #1: Prohození Fan RPM registrů
V `const.py` řádky 57-59:
```python
# PŘED:
REG_DC_FAN1_OUTPUT = 199  # 40200
REG_DC_FAN1_FEEDBACK = 200  # 40201
REG_DC_FAN2_OUTPUT = 201  # 40202
REG_DC_FAN2_FEEDBACK = 202  # 40203

# PO:
REG_DC_FAN1_OUTPUT = 199  # 40200
REG_DC_FAN1_FEEDBACK = 202  # 40203 - Fan1 RPM podle tabulky
REG_DC_FAN2_OUTPUT = 201  # 40202
REG_DC_FAN2_FEEDBACK = 200  # 40201 - Fan2 RPM podle tabulky
```

### Oprava #2: Testování Unit_COP formátu
Zkusit přečíst 19 registrů a Unit_COP jako 32-bit float:
```python
# V __init__.py, změnit z 18 na 19 registrů:
power_regs = await hass.async_add_executor_job(
    client.read_holding_registers_bulk, REG_WATER_FLOW, 19, 0, slave_id, True  # raw=True, změněno z 18 na 19
)
if power_regs and len(power_regs) == 19:
    # ...
    # Vyzkoušet Unit COP jako float32:
    data["unit_cop"] = registers_to_float32(power_regs[17], power_regs[18])
```
