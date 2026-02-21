# EcoFlow Cloud Alt (EU + Alternator Charger)

Fork of [hassio-ecoflow-cloud-US](https://github.com/snell-evan-itt/hassio-ecoflow-cloud-US) with:

✅ **EU endpoint** (api-e.ecoflow.com) - works with European EcoFlow accounts  
✅ **Alternator Charger support** - full MQTT support for 500W/800W models  
✅ **Production-tested** - based on working installation

## Installation

### Via HACS (recommended)

1. HACS → Integrations → ⋮ → Custom repositories
2. Add: `https://github.com/artemkudriashov/ecoflow-ha-alt`
3. Category: Integration
4. Download "EcoFlow Cloud (EU + Alternator Charger)"
5. Restart Home Assistant
6. Settings → Add Integration → search "EcoFlow Cloud (EU"
7. Enter your EcoFlow API keys

### Manual

1. Copy `custom_components/ecoflow_cloud_alt` to your HA `custom_components/`
2. Restart HA
3. Add integration via UI

## Supported Devices

All devices from original integration, **PLUS:**

### ⚡ Alternator Charger (500W/800W)

**Sensors (9):**
- Battery Level (%)
- Battery Temperature (°C)
- DC Power (W)
- Car Battery Voltage (V)
- Charging Current Limit (A)
- Reverse Charging Current Limit (A)
- Power Limit (W)
- Max Power (W)
- Status

**Switches (2):**
- Charger (on/off)
- Emergency Reverse Charging

**Numbers (2):**
- Start Voltage (11-31V)
- Power Limit (0-800W)

**Select (1):**
- Charger Mode (Idle/Charge/Maintenance/Reverse)

## Differences from Original

1. **EU endpoint** - uses `api-e.ecoflow.com` instead of `api-a.ecoflow.com`
2. **Alternator Charger** - added full support for this MQTT-only device
3. **Relaxed productName check** - handles devices without productName field
4. **Domain renamed** - `ecoflow_cloud_alt` to avoid conflicts

## API Keys

Get your keys from: https://developer.ecoflow.com/us/security

**Important:** Must use **EU** endpoint if your EcoFlow account is European.

## Credits

- Original: [@snell-evan-itt](https://github.com/snell-evan-itt/hassio-ecoflow-cloud-US)
- Based on: [@tolwi/hassio-ecoflow-cloud](https://github.com/tolwi/hassio-ecoflow-cloud)
- Alternator Charger protocol: [@rabits/ha-ef-ble](https://github.com/rabits/ha-ef-ble)

## License

Same as original project.
