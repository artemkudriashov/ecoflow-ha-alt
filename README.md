# EcoFlow Cloud Alt (EU + Alternator Charger)

Home Assistant інтеграція для пристроїв EcoFlow з підтримкою **EU API** та **Alternator Charger**.

Базується на [hassio-ecoflow-cloud-US](https://github.com/snell-evan-itt/hassio-ecoflow-cloud-US) з покращеннями для європейських користувачів.

## ✨ Особливості

✅ **EU API endpoint** - працює з європейськими EcoFlow акаунтами  
✅ **Alternator Charger (500W/800W)** - повна підтримка через protobuf MQTT  
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

### ⚡ Alternator Charger (500W/800W)

**Унікальна особливість цієї інтеграції!**

Повна підтримка через protobuf MQTT:

**Сенсори (8):**
- Battery Level (%)
- Temperature (°C)
- Alternator Power (W)
- Station Power (W)
- Car Battery Voltage (V)
- Rated Power (W)
- Charging Time (min)
- Status

**Керування (5):**
- Start Voltage (11-30V) - поріг увімкнення
- Power Limit (0-800W) - обмеження потужності
- Cable Length (0-10m) - компенсація втрат
- Operation Mode - режим роботи:
  - Charge (зарядка від авто)
  - Battery Maintenance (підтримка)
  - Reverse Charge (зарядка авто від станції)
- Start/Stop Switch - увімкнути/вимкнути

## 🆚 Відмінності від оригінальної інтеграції

| Особливість | Оригінал (US) | EcoFlow Cloud Alt |
|-------------|---------------|-------------------|
| API Endpoint | US (`api-a`) | **EU (`api-e`)** |
| Alternator Charger | ❌ | ✅ Protobuf підтримка |
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
2. Не публікує MQTT дані - можливо треба запустити зарядку
3. Використовується старий firmware - оновіть через app

**Перевірка:**
1. Settings → System → Logs
2. Шукай `ecoflow_cloud_alt`
3. Дивись чи є `Subscribed to MQTT topics` з `F371...` (серійний номер)
4. Дивись чи приходять `Message for F371...`

### Показує "Unavailable"

Alternator Charger **може не публікувати дані постійно** - тільки під час активної роботи (зарядка від авто). Це нормально.

## 📚 Технічні деталі

### Протоколи

- **Delta/River/PowerStream**: JSON через MQTT
- **Alternator Charger**: Protobuf через MQTT (cmdFunc: 254, cmdId: 21)

### MQTT Топіки

```
/open/{clientId}/{deviceSN}/quota    # Дані з пристрою
/open/{clientId}/{deviceSN}/set      # Команди до пристрою
/open/{clientId}/{deviceSN}/set_reply # Підтвердження команд
/open/{clientId}/{deviceSN}/status   # Статус пристрою
```

### Protobuf повідомлення (Alternator Charger)

Використовується `alternatorHeartbeat` message з полями:
- `batSoc` (float)
- `temp` (int32)
- `alternatorPower` (float)
- `carBatVolt` (float)
- `stationPower` (float)
- `operationMode` (int32)
- та інші

Повний protobuf schema в коді: `devices/public/alternator_charger.py`

## 🙏 Подяки

- Оригінальна інтеграція: [@snell-evan-itt/hassio-ecoflow-cloud-US](https://github.com/snell-evan-itt/hassio-ecoflow-cloud-US)
- Базова версія: [@tolwi/hassio-ecoflow-cloud](https://github.com/tolwi/hassio-ecoflow-cloud)
- Alternator Charger protobuf: [@foxthefox/ioBroker.ecoflow-mqtt](https://github.com/foxthefox/ioBroker.ecoflow-mqtt)

## 📄 Ліцензія

MIT License - використовуйте вільно!

## ⚠️ Disclaimer

Це неофіційна інтеграція, не пов'язана з компанією EcoFlow. Використання на власний ризик.

---

**Підтримка:** [Issues](https://github.com/artemkudriashov/ecoflow-ha-alt/issues)  
**Автор:** [@artemkudriashov](https://github.com/artemkudriashov)
