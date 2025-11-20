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

### Chyba #2: Unit_COP Špatné Mapování v Bulkovém Čtení ✓ OPRAVENO
**Problém:** Unit_COP nefungoval po včerejším update.

Podle tabulky:
- Unit_COP: add=389, modbus=40390, **byte=1**, data type=real

**Příčina:**
Po včerejších změnách se změnila struktura bulkového čtení a Unit_COP se nečetl správně.

**Testováno:**
1. ✗ 32-bit IEEE 754 float (2 registry) - zobrazilo 8.39e-43 (nesmysl)
2. ✓ 16-bit signed / 10 (1 registr) - funguje, zobrazuje správnou hodnotu ~3.0

**Závěr:**
Tabulka výrobce je **správná** - Unit_COP je 1 registr (16-bit signed) s přesností 0.1.

**Oprava:**
1. `const.py` řádek 159: Potvrzen komentář, Unit_COP je 1 registr s 0.1 precision
2. `__init__.py` řádek 330-334: Bulkové čtení 18 registrů (372-389)
3. `__init__.py` řádek 371-372: Unit_COP čten jako 16-bit signed / 10

## Testování

### Před testem:
1. Restartujte Home Assistant
2. Počkejte na první update dat (30 sekund)

### Co kontrolovat:
1. ✓ **sensor.sprsun_unit_cop** - zobrazuje správnou hodnotu ~3.0 (16-bit scaled formát)
2. ✓ **sensor.sprsun_dc_fan1_feedback** - Fan1 RPM (registr 202)
3. ✓ **sensor.sprsun_dc_fan2_feedback** - Fan2 RPM (registr 200)

### Poznámka k Unit_COP:
Otestovali jsme oba formáty:
- **32-bit float** ❌ zobrazovalo 8.39e-43 (nesmysl)
- **16-bit scaled** ✓ funguje správně (hodnota ~3.0)

Tabulka výrobce je správná - Unit_COP je 1 registr s 0.1 precision.

## Souhrn Změn

### Soubory upraveny:
1. `custom_components/sprsun_modbus/const.py`
   - Řádek 57-59: Opraveny Fan1/Fan2 RPM registry (prohozeny podle tabulky)
   - Řádek 159: Potvrzen komentář pro Unit_COP (1 registr, 0.1 precision)

2. `custom_components/sprsun_modbus/__init__.py`
   - Řádek 178-180: Opraveno mapování Fan1/Fan2 feedback (prohozeny indexy)
   - Řádek 330-334: Bulkové čtení 18 registrů (372-389)
   - Řádek 371-372: Unit_COP čten jako 16-bit signed / 10

### Nové soubory:
1. `validate_register_mapping.md` - Kompletní validace všech registrů
2. `test_unit_cop.py` - Testovací skript pro Unit_COP formáty
3. `OPRAVY_MODBUS_REGISTRU.md` - Tento dokument

## Další Senzory
Podle kontroly jsou ostatní senzory správně namapované. Pokud nefungují další senzory, zkontrolujte:
- Home Assistant logy pro modbus chyby
- Konektivitu k zařízení (modbus slave ID, baud rate, atd.)

---

## Update 2025-11-20: Oprava Unit Power podle verze 1.0.1

### Chyba #3: Unit Power Špatný Formát ✓ OPRAVENO

**Problém:** Unit Power byl čten jako 2x 16-bit scaled hodnoty (kW * 1000 + W), což neodpovídá oficiální dokumentaci.

**Podle tabulky:**
- Unit Power: add=387, modbus=40388, **byte=2**, data type=**REAL** (IEEE 754 float32)

**Původní implementace (CHYBNÁ):**
```python
# Registr 387 = kW (tisíce wattů), Registr 388 = W (jednotky/stovky)
unit_power_kw_raw = power_regs[15]  # reg 387
unit_power_w_raw = power_regs[16]   # reg 388
data["unit_power"] = float(unit_power_kw_raw * 1000 + unit_power_w_raw)
```

**Nová implementace (SPRÁVNÁ):**
```python
# Unit power (387-388, 2 registers REAL/FLOAT32)
# According to official documentation: add=387, byte=2, type=REAL (IEEE 754 float32)
unit_power_raw = registers_to_float32(power_regs[15], power_regs[16])
data["unit_power"] = unit_power_raw if unit_power_raw is not None else None
```

**Oprava:**
- `__init__.py` řádky 367-370: Unit Power nyní čten jako IEEE 754 float32

**Co testovat:**
- **sensor.sprsun_unit_power** - měl by zobrazovat správnou hodnotu příkonu jednotky ve Wattech
