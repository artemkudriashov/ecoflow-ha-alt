# EcoFlow Cloud Alt (EU + Alternator Charger)

Home Assistant інтеграція для пристроїв EcoFlow з підтримкою **EU API** та **Alternator Charger**.

Базується на [hassio-ecoflow-cloud-US](https://github.com/snell-evan-itt/hassio-ecoflow-cloud-US) з покращеннями для європейських користувачів.

## ✨ Особливості

✅ **EU API endpoint** - працює з європейськими EcoFlow акаунтами  
✅ **Alternator Charger (500W/800W)** - **ПОВНА ПІДТРИМКА** з керуванням! ⚡  
✅ **Всі стандартні пристрої** - Delta, River, PowerStream, Wave, Glacier тощо  
✅ **Production-ready** - протестовано на реальних пристроях  

## 🔧 Встановлення

### Через HACS (рекомендовано)

1. HACS → Integrations → ⋮ (три крапки) → Custom repositories
2. Додай репозиторій: `https://github.com/artemkudriashov/ecoflow-ha-alt`
3. Category: **Integration**
4. Натисни **Add**
5. Знайди **"EcoFlow Cloud Alt"** в списку
6. **Download**
7. **Restart Home Assistant**
8. Settings → Devices & Services → **Add Integration**
9. Шукай **"EcoFlow Cloud Alt"**
10. Введи свої EcoFlow API ключі

### Вручну

1. Скопіюй папку `custom_components/ecoflow_cloud_alt` в свою теку `custom_components/`
2. Restart Home Assistant
3. Settings → Devices & Services → Add Integration → EcoFlow Cloud Alt

## 🔑 API Ключі

Отримай ключі з [EcoFlow Developer Portal](https://developer.ecoflow.com/us/security):

1. Зареєструйся (використовуй той самий акаунт що в EcoFlow app)
2. Створи API ключі
3. Скопіюй **AccessKey** та **SecretKey**

**⚠️ Важливо:** Для європейських акаунтів інтеграція автоматично використовує **EU endpoint** (`api-e.ecoflow.com`).

## 📱 Підтримувані пристрої

### Всі стандартні пристрої:
- **Delta Series**: Delta Pro, Delta 2, Delta 2 Max, Delta Mini
- **River Series**: River 2, River 2 Max, River 2 Pro, River Max, River Pro
- **PowerStream** 600W/800W
- **Smart Plug**
- **Wave 2** / **Wave 3** (кондиціонери)
- **Glacier** (холодильники)

### ⚡ Alternator Charger (500W/800W) - ПОВНА ПІДТРИМКА! 🎉

**Унікальна особливість цієї інтеграції!**

Єдина Home Assistant інтеграція з **повним керуванням** Alternator Charger через protobuf MQTT.

#### Що працює ✅

**Моніторинг (real-time):**
- 🔋 Battery Level (%)
- 🌡️ Temperature (°C)
- ⚡ Alternator Power (W) - потужність заряду від авто
- 🔌 Station Power (W) - потужність на виході
- 🚗 Car Battery Voltage (V)
- 📊 Rated Power (W) - максимальна потужність
- ⏱️ Charging Time (min)
- 🟢 Status (online/offline)
- 📶 WiFi Signal (RSSI)

**Керування (працює!):**
- 🔴 **Start/Stop Switch** - увімкнути/вимкнути зарядку
- 🎛️ **Operation Mode** - вибір режиму роботи:
  - **Charge** - зарядка станції від авто (через генератор)
  - **Battery Maintenance** - підтримка заряду авто батареї
  - **Reverse Charge** - зарядка авто батареї від станції
- ⚙️ **Power Limit** (0-800W) - обмеження потужності заряду
- 🔌 **Start Voltage** (11-30V) - поріг напруги для автостарту
- 📏 **Cable Length** (0-10m) - компенсація втрат на кабелі

#### Приклади використання

**Автоматизація в дорозі:**
```yaml
automation:
  - alias: "Авто-зарядка станції від генератора"
    trigger:
      - platform: numeric_state
        entity_id: sensor.alternator_charger_car_battery_voltage
        above: 13.5  # Двигун працює
    condition:
      - condition: numeric_state
        entity_id: sensor.alternator_charger_battery_level
        below: 80
    action:
      - service: switch.turn_on
        entity_id: switch.alternator_charger_start_stop
      - service: select.select_option
        data:
          entity_id: select.alternator_charger_operation_mode
          option: "Charge"
```

**Підзарядка авто батареї:**
```yaml
automation:
  - alias: "Підтримка авто батареї вночі"
    trigger:
      - platform: time
        at: "02:00:00"
    condition:
      - condition: numeric_state
        entity_id: sensor.alternator_charger_car_battery_voltage
        below: 12.4  # Розряджена авто батарея
    action:
      - service: switch.turn_on
        entity_id: switch.alternator_charger_start_stop
      - service: select.select_option
        data:
          entity_id: select.alternator_charger_operation_mode
          option: "Battery Maintenance"
```

## 🆚 Відмінності від оригінальної інтеграції

| Особливість | Оригінал (US) | EcoFlow Cloud Alt |
|-------------|---------------|-------------------|
| API Endpoint | US (`api-a`) | **EU (`api-e`)** |
| Alternator Charger | ❌ Не підтримується | ✅ **Повна підтримка** (читання + керування) |
| Protobuf MQTT | ❌ | ✅ З XOR шифруванням |
| Пристрої без `productName` | ❌ Відкидає | ✅ Авто-визначення |
| Domain | `ecoflow_cloud` | `ecoflow_cloud_alt` |

**Domain змінено** щоб уникнути конфліктів - можна встановити обидві інтеграції одночасно.

## 🛠️ Налаштування

Після встановлення:

1. Settings → Devices & Services
2. Знайди **EcoFlow Cloud Alt**
3. Натисни **Configure**
4. Обери пристрої які хочеш додати
5. Налаштуй параметри (опціонально):
   - Refresh period (за замовчуванням: 5 сек)
   - Power step (за замовчуванням: 100W)

## 🔍 Діагностика

### Інтеграція не бачить Alternator Charger

**Можливі причини:**
1. Пристрій offline - перевір WiFi підключення в EcoFlow app
2. Не публікує MQTT дані - можливо треба один раз запустити зарядку через app
3. Використовується старий firmware - оновіть через app

**Перевірка:**
1. Settings → System → Logs
2. Шукай `ecoflow_cloud_alt`
3. Дивись чи є `Subscribed to MQTT topics` з `F371...` (серійний номер)
4. Дивись чи приходять `Message for F371...`

### Керування не працює

**Якщо бачиш дані але не працюють команди:**

1. **Перевір логи:** `Settings → System → Logs → ecoflow_cloud_alt`
2. Шукай `Encoded Alternator command` - якщо бачиш, команда надіслана
3. Шукай `Command response detected` - якщо бачиш, пристрій відповів
4. Якщо бачиш `Failed to decode` - це нормально для ACK повідомлень

**Важливо:** Alternator Charger може **ігнорувати команди** якщо:
- Напруга авто батареї за межами допустимого (< 11V або > 30V)
- Пристрій в режимі захисту (перегрів, перевантаження)
- WiFi з'єднання нестабільне

### Показує "Unavailable"

Alternator Charger **може не публікувати дані постійно** - тільки під час активної роботи або коли підключений до авто. Це нормальна поведінка пристрою.

**Щоб пристрій "прокинувся":**
1. Підключи до авто батареї
2. Один раз увімкни через EcoFlow app
3. Після цього інтеграція побачить пристрій

## 📚 Технічні деталі

### Протоколи

- **Delta/River/PowerStream**: JSON через MQTT
- **Alternator Charger**: **Protobuf через MQTT** з XOR шифруванням

### MQTT Топіки

**Для Alternator Charger (Private API):**
```
/app/{userId}/{deviceSN}/thing/property/get     # Читання даних
/app/{userId}/{deviceSN}/thing/property/set     # Команди
/app/device/property/{deviceSN}                  # Heartbeat (дані)
```

**Для інших пристроїв (Public API):**
```
/open/{clientId}/{deviceSN}/quota               # Дані з пристрою
/open/{clientId}/{deviceSN}/set                 # Команди до пристрою
/open/{clientId}/{deviceSN}/set_reply           # Підтвердження команд
/open/{clientId}/{deviceSN}/status              # Статус пристрою
```

### Protobuf структура (Alternator Charger)

**Heartbeat (читання):**
```protobuf
message alternatorHeartbeat {
  optional int32 status1 = 1;
  optional int32 temp = 102;
  optional float alternatorPower = 105;  // XOR encrypted with seq
  optional float carBatVolt = 139;
  optional float stationPower = 425;
  optional int32 operationMode = 581;    // 1=Charge, 2=Maintenance, 3=Reverse
  optional int32 startStop = 597;        // 0=off, 1=on
  optional float permanentWatts = 598;
  // ... інші поля
}
```

**Commands (керування):**
```protobuf
message setMessage {
  setHeader header = 1;
}

message setHeader {
  optional alternatorSet pdata = 1;  // NOT XOR encrypted!
  int32 src = 2;                     // 32
  int32 dest = 3;                    // 20
  int32 cmd_func = 8;                // 254
  int32 cmd_id = 9;                  // 17
  int32 seq = 14;                    // timestamp
  // ... інші поля
}

message alternatorSet {
  optional int32 operationMode = 116;  // NOTE: Different field# than heartbeat!
  optional int32 startStop = 122;
  optional float permanentWatts = 123;
  optional int32 startVoltage = 137;   // * 10 (110 = 11.0V)
  // ... інші поля
}
```

**Ключові особливості:**
- **XOR шифрування** тільки для heartbeat (pdata XOR seq)
- **Різні field numbers** для команд (116/122/123) vs heartbeat (581/597/598)
- Command responses **НЕ шифруються** XOR (seq > 100000000 = timestamp)
- Знак потужності **інвертований** (EcoFlow репортує output як негативний)

Повний код: `devices/proto/alternator_pb.py`

## 🐛 Відомі проблеми

### Alternator Charger іноді втрачає з'єднання

**Симптом:** Entity стає `unavailable`, потім через кілька хвилин повертається.

**Причина:** Пристрій переходить в режим енергозбереження коли не використовується.

**Рішення:** Це нормальна поведінка. Пристрій "прокинеться" при:
- Підключенні до авто батареї
- Зміні напруги на вході
- Увімкненні через app

### Power показує 0W коли пристрій працює

**Причина:** Низька потужність (< 10W) може округлюватись до 0.

**Перевірка:** Дивись `Car Battery Voltage` - якщо змінюється, зарядка працює.

## 🙏 Подяки

- Оригінальна інтеграція: [@snell-evan-itt/hassio-ecoflow-cloud-US](https://github.com/snell-evan-itt/hassio-ecoflow-cloud-US)
- Базова версія: [@tolwi/hassio-ecoflow-cloud](https://github.com/tolwi/hassio-ecoflow-cloud)
- **Alternator Charger protobuf:** [@foxthefox/ioBroker.ecoflow-mqtt](https://github.com/foxthefox/ioBroker.ecoflow-mqtt) - дякую за reverse engineering! 🙏

## 📝 Changelog

### v1.1.0 (2026-02-22) - Alternator Charger WORKS! 🎉

**Нові можливості:**
- ✅ **Повне керування Alternator Charger** (start/stop, режими роботи)
- ✅ Правильний protobuf encoding з full setMessage structure
- ✅ Command response decoding (без XOR для timestamp seq)
- ✅ Інверсія знаку потужності (output тепер позитивний)

**Виправлення:**
- 🐛 Field numbers для команд (116/122/123 замість 581/597/598)
- 🐛 BaseSelectEntity type в alternator_charger.py
- 🐛 Декодування command responses (великий seq > 100M без XOR)

**Технічні деталі:**
- Базується на дослідженні [ioBroker.ecoflow-mqtt](https://github.com/foxthefox/ioBroker.ecoflow-mqtt)
- 6+ годин reverse engineering 😅
- Протестовано на реальному Alternator Charger 800W

### v1.0.0 - Початковий реліз
- EU API endpoint
- Базова підтримка Alternator Charger (тільки читання)
- Всі стандартні пристрої

## 📄 Ліцензія

MIT License - використовуйте вільно!

## ⚠️ Disclaimer

Це неофіційна інтеграція, не пов'язана з компанією EcoFlow. Використання на власний ризик.

EcoFlow® та назви продуктів є торговими марками EcoFlow Inc.

---

**Підтримка:** [Issues](https://github.com/artemkudriashov/ecoflow-ha-alt/issues)  
**Автор:** [@artemkudriashov](https://github.com/artemkudriashov)  

**⭐ Якщо інтеграція вам допомогла - поставте зірочку на GitHub! ⭐**
