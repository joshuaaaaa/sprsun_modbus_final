# SPRSUN Heat Pump Modbus Integration for Home Assistant

Integrace pro Home Assistant umožňující ovládání a monitoring tepelných čerpadel SPRSUN přes Modbus RTU (sériové i TCP/UDP připojení).

## Funkce

- **Monitoring teploty**: vstupní, výstupní, okolní, teplá voda, výparník, kondenzátor
- **Monitoring tlaku**: sání, výtlak
- **Ovládání vytápění/chlazení**: nastavení teploty, režim práce
- **Monitorování výkonu**: BLDC motor (výkon, napětí, proud)
- **Alarmy**: monitoring všech systémových alarmů
- **Režimy ventilátoru**: denní, noční, nízké otáčky, tlakový
- **Režimy čerpadla**: normální, na požádání, intervalový

## Požadavky

- Home Assistant 2023.1 nebo novější
- PyModbus 3.6.2
- Modbus RTU spojení (USB-RS485 nebo TCP-RS485 převodník)
- Tepelné čerpadlo SPRSUN s Modbus podporou (testováno na CGK0x0V2)

## Instalace

### HACS (doporučeno)

1. Otevřete HACS v Home Assistant
2. Přejděte na "Integrace"
3. Klikněte na tři tečky v pravém horním rohu a vyberte "Vlastní repositáře"
4. Přidejte URL tohoto repositáře
5. Vyhledejte "SPRSUN Heat Pump Modbus" a nainstalujte
6. Restartujte Home Assistant

### Manuální instalace

1. Zkopírujte složku `sprsun_modbus` do `custom_components` v konfigurační složce Home Assistant
2. Restartujte Home Assistant

## Konfigurace

1. Přejděte na Nastavení → Zařízení a služby
2. Klikněte na tlačítko "+ PŘIDAT INTEGRACI"
3. Vyhledejte "SPRSUN Heat Pump Modbus"
4. Vyberte typ připojení:
   - **RTU-Serial**: pro přímé USB-RS485 připojení
   - **RTU-TCP**: pro TCP-RS485 převodník (např. ZLAN 5143D)
   - **RTU-UDP**: pro UDP-RS485 převodník

### Parametry pro sériové připojení

- **Sériový port**: např. `/dev/ttyUSB0`
- **Přenosová rychlost**: výchozí 19200
- **Slave ID**: výchozí 1

### Parametry pro TCP/UDP připojení

- **IP adresa**: adresa TCP/UDP převodníku
- **Port**: výchozí 502
- **Slave ID**: výchozí 1

## Entity

Po úspěšné konfiguraci budou vytvořeny následující entity:

### Senzory (sensor)

- Teploty: vstupní, výstupní, okolní, teplá voda, výparník, kondenzátor, vinutí
- Tlaky: sání, výtlak
- Výstupy: ventilátor, čerpadlo
- Kapacita: požadovaná, aktuální
- BLDC motor: výkon, napětí, proud
- Stav jednotky

### Ovládání (climate)

- Hlavní ovládací panel tepelného čerpadla
- Režimy: vytápění, chlazení, automatické
- Nastavení cílové teploty

### Přepínače (switch)

- Zapnutí/vypnutí jednotky

### Výběry (select)

- Pracovní režim: chlazení, vytápění, teplá voda, kombinace
- Režim ventilátoru: denní, noční, nízké otáčky, tlakový
- Režim čerpadla: normální, na požádání, intervalový

### Čísla (number)

- Teplota vytápění (setpoint)
- Teplota chlazení (setpoint)
- Teplota teplé vody (setpoint)
- Teplotní rozdíl teplé vody
- Teplotní rozdíl vytápění/chlazení

### Binární senzory (binary_sensor)

- Stav čerpadla
- Stav ventilátoru (vysoké/nízké otáčky)
- Stav 4-cestného ventilu
- Stav ohřívače
- Stav 3-cestného ventilu
- Průtokoměr
- Systémové alarmy (více než 100 různých alarmů)

## Modbus Registry

Integrace využívá následující Modbus registry:

### Holding Registry (čtení/zápis)

- `40001` - Pracovní režim (0-4)
- `40002` - Teplota vytápění (0.1°C)
- `40003` - Teplota chlazení (0.1°C)
- `40004` - Teplota teplé vody (0.1°C)
- `40189` - Vstupní teplota (0.1°C)
- `40190` - Výstupní teplota (0.1°C)
- `40191` - Okolní teplota (0.1°C)
- ... a další

### Coils (čtení/zápis)

- `00041` - Zapnutí/vypnutí jednotky
- ... a další

### Discrete Inputs (pouze čtení)

- `10002` - Průtokoměr
- `10014+` - Alarmy
- ... a další

Kompletní seznam registrů je v souboru `const.py`.

## Podpora

Pro problémy a dotazy vytvořte issue na GitHubu.

## Licence

MIT License

## Autoři

- Původní Domoticz plugin: Sateetje
- Home Assistant integrace: https://github.com/joshuaaaaa/sprsun_modbus

## Poznámky

- Testováno s tepelným čerpadlem SPRSUN CGK0x0V2
- Používá PyModbus 3.6.2
- Interval aktualizace: 30 sekund (konfigurovatelné)
- Při změně pracovního režimu je nutné jednotku vypnout a znovu zapnout

## Changelog

### 1.0.0
-初始發布
- Podpora pro RTU-Serial, RTU-TCP, RTU-UDP
- Všechny základní funkce a monitorování
- České překlady


## Support

If you like this card, please ⭐ star this repository!

Found a bug or have a feature request? Please open an issue.



## http://buymeacoffee.com/jakubhruby


<img width="150" height="150" alt="qr-code" src="https://github.com/user-attachments/assets/2581bf36-7f7d-4745-b792-d1abaca6e57d" />
