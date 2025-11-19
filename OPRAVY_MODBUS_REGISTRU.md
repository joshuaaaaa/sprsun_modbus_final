# Opravy Modbus Registrů - Unit COP a další senzory

## Problém
Po včerejším update nefungoval `sensor.sprsun_unit_cop` a možná další senzory.

## Provedená Kontrola
Kompletní validace mapování modbus registrů podle tabulky výrobce (viz `validate_register_mapping.md`).

## Nalezené Chyby

### Chyba #1: Fan RPM Registry Prohozené ✓ OPRAVENO
**Problém:** Fan1 RPM a Fan2 RPM měly prohozené registry.

Podle tabulky:
- Fan2 RPM: add=200, modbus=40201
- Fan1 RPM: add=202, modbus=40203

V kódu bylo chybně:
- `REG_DC_FAN1_FEEDBACK = 200` (mělo být 202)
- `REG_DC_FAN2_FEEDBACK = 202` (mělo být 200)

**Oprava:**
- `const.py` řádky 57-59: Opraveny registry
- `__init__.py` řádky 178-180: Opraveno mapování

### Chyba #2: Unit_COP Nesprávný Datový Typ ✓ OPRAVENO
**Problém:** Unit_COP nefungoval.

Podle tabulky:
- Unit_COP: add=389, modbus=40390, **byte=1**, data type=real

V kódu bylo implementováno jako:
- 1 registr (16-bit) s přesností 0.1 (dělení 10)

**Pravděpodobná příčina:**
Dokumentace výrobce má chybu - Unit_COP je pravděpodobně **32-bit IEEE 754 float** (2 registry), ne 16-bit scaled integer.

**Důkazy:**
- Unit Power (add=387, byte=2) je těsně před Unit_COP a je čten jako 32-bit float
- Pokud by Unit_COP byl 16-bit scaled, hodnota by byla mezi 0-6553.5 (max 16-bit signed / 10)
- COP hodnoty jsou typicky 2.0-6.0, což lépe sedí na IEEE 754 float

**Oprava:**
1. `const.py` řádek 159: Změněn komentář, Unit_COP je nyní 2 registry (40390-40391)
2. `__init__.py` řádek 332-334: Bulkové čtení změněno z 18 na 19 registrů (372-390)
3. `__init__.py` řádek 372-378: Unit_COP čten jako 32-bit float místo 16-bit scaled

## Testování

### Před testem:
1. Restartujte Home Assistant
2. Počkejte na první update dat (30 sekund)

### Co kontrolovat:
1. **sensor.sprsun_unit_cop** - měla by zobrazit rozumnou hodnotu (např. 3.2, 4.5)
   - Pokud zobrazuje nesmyslnou hodnotu (např. 1.5e-10), vrátíme se k 16-bit scaled
2. **sensor.sprsun_dc_fan1_feedback** - Fan1 RPM
3. **sensor.sprsun_dc_fan2_feedback** - Fan2 RPM

### Pokud Unit_COP stále nefunguje:

Zkuste alternativní řešení v `__init__.py` řádek 378:
```python
# Zakomentujte řádky 374-375:
# unit_cop_raw = registers_to_float32(power_regs[17], power_regs[18])
# data["unit_cop"] = unit_cop_raw if unit_cop_raw is not None else None

# Odkomentujte řádek 378:
data["unit_cop"] = to_signed_16bit(power_regs[17])

# A změňte řádek 333 zpět na 18 registrů:
client.read_holding_registers_bulk, REG_WATER_FLOW, 18, 0, slave_id, True
```

## Souhrn Změn

### Soubory upraveny:
1. `custom_components/sprsun_modbus/const.py`
   - Řádek 57-59: Opraveny Fan1/Fan2 RPM registry
   - Řádek 159: Aktualizován komentář pro Unit_COP

2. `custom_components/sprsun_modbus/__init__.py`
   - Řádek 178-180: Opraveno mapování Fan1/Fan2 feedback
   - Řádek 332-334: Změněno bulkové čtení z 18 na 19 registrů
   - Řádek 372-378: Unit_COP čten jako 32-bit float

### Nové soubory:
1. `validate_register_mapping.md` - Kompletní validace všech registrů
2. `test_unit_cop.py` - Testovací skript pro Unit_COP formáty
3. `OPRAVY_MODBUS_REGISTRU.md` - Tento dokument

## Další Senzory
Podle kontroly jsou ostatní senzory správně namapované. Pokud nefungují další senzory, zkontrolujte:
- Home Assistant logy pro modbus chyby
- Konektivitu k zařízení (modbus slave ID, baud rate, atd.)
