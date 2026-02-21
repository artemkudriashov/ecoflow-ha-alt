from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from .data_bridge import to_plain

from custom_components.ecoflow_cloud_alt import EcoflowApiClient
from custom_components.ecoflow_cloud_alt.devices import BaseDevice, const
from custom_components.ecoflow_cloud_alt.sensor import (
    LevelSensorEntity,
    TempSensorEntity,
    InWattsSensorEntity,
    VoltSensorEntity,
    AmpSensorEntity,
    StatusSensorEntity
)
from custom_components.ecoflow_cloud_alt.switch import EnabledEntity
from custom_components.ecoflow_cloud_alt.number import MaxBatteryLevelEntity
from custom_components.ecoflow_cloud_alt.select import DictSelectEntity


class AlternatorCharger(BaseDevice):
    """EcoFlow Alternator Charger device (500W/800W).
    
    MQTT-only device - does not support REST API quota/all.
    """

    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            # Battery sensors
            LevelSensorEntity(client, self, "cms_batt_soc", const.BATTERY_LEVEL),
            TempSensorEntity(client, self, "cms_batt_temp", const.BATTERY_TEMP),
            
            # Power and voltage
            InWattsSensorEntity(client, self, "pow_get_dc_bidi", "DC Power"),
            VoltSensorEntity(client, self, "sp_charger_car_batt_vol", "Car Battery Voltage"),
            
            # Current limits
            AmpSensorEntity(client, self, "sp_charger_dev_batt_chg_amp_limit", "Charging Current Limit"),
            AmpSensorEntity(client, self, "sp_charger_car_batt_chg_amp_limit", "Reverse Charging Current Limit"),
            
            # Power limit
            InWattsSensorEntity(client, self, "sp_charger_chg_pow_limit", "Power Limit"),
            InWattsSensorEntity(client, self, "sp_charger_chg_pow_max", "Max Power", False),
            
            # Status
            StatusSensorEntity(client, self)
        ]

    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        return [
            # Start voltage (11V - 31V)
            MaxBatteryLevelEntity(
                client, self, 
                "sp_charger_car_batt_vol_setting", 
                "Start Voltage",
                11, 31,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "WN511_SET_START_VOLTAGE",
                    "params": {"cfg_sp_charger_car_batt_vol_setting": int(value * 10)}
                }
            ),
            
            # Power limit
            MaxBatteryLevelEntity(
                client, self,
                "sp_charger_chg_pow_limit",
                "Power Limit",
                0, 800,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "WN511_SET_POWER_LIMIT",
                    "params": {"cfg_sp_charger_chg_pow_limit": int(value)}
                }
            ),
        ]

    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        return [
            # Charger on/off
            EnabledEntity(
                client, self,
                "sp_charger_chg_open",
                "Charger",
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "WN511_SET_CHARGER_OPEN",
                    "params": {"cfg_sp_charger_chg_open": value}
                }
            ),
            
            # Emergency reverse charging
            EnabledEntity(
                client, self,
                "sp_charger_car_batt_urgent_chg_switch",
                "Emergency Reverse Charging",
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "WN511_SET_EMERGENCY_REVERSE",
                    "params": {"cfg_sp_charger_car_batt_urgent_chg_switch": value}
                }
            )
        ]

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        # Charger modes
        modes = {
            0: "Idle",
            1: "Charge (Driving)",
            2: "Battery Maintenance",
            3: "Reverse Charge (Parking)"
        }
        
        return [
            DictSelectEntity(
                client, self,
                "sp_charger_chg_mode",
                "Charger Mode",
                modes,
                lambda value: {
                    "sn": self.device_info.sn,
                    "cmdCode": "WN511_SET_CHARGER_MODE",
                    "params": {"cfg_sp_charger_chg_mode": value}
                }
            )
        ]

    def _prepare_data(self, raw_data) -> dict[str, any]:
        res = super()._prepare_data(raw_data)
        res = to_plain(res)
        return res
