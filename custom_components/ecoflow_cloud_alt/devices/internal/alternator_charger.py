from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity

from custom_components.ecoflow_cloud_alt import EcoflowApiClient
from custom_components.ecoflow_cloud_alt.devices import BaseDevice, const
from custom_components.ecoflow_cloud_alt.sensor import (
    LevelSensorEntity,
    TempSensorEntity,
    InWattsSensorEntity,
    VoltSensorEntity,
    RemainSensorEntity,
    StatusSensorEntity
)
from custom_components.ecoflow_cloud_alt.switch import EnabledEntity
from custom_components.ecoflow_cloud_alt.number import MaxBatteryLevelEntity, MinBatteryLevelEntity
from custom_components.ecoflow_cloud_alt.select import DictSelectEntity


class AlternatorCharger(BaseDevice):
    """EcoFlow Alternator Charger device (500W/800W).
    
    Cloud MQTT supported device.
    Based on ioBroker.ecoflow-mqtt alternator implementation.
    """

    def sensors(self, client: EcoflowApiClient) -> list[SensorEntity]:
        return [
            # Battery
            LevelSensorEntity(client, self, "batSoc", const.MAIN_BATTERY_LEVEL),
            
            # Temperature
            TempSensorEntity(client, self, "temp", const.BATTERY_TEMP),
            
            # Power
            InWattsSensorEntity(client, self, "alternatorPower", "Alternator Power"),
            InWattsSensorEntity(client, self, "stationPower", "Station Power"),
            InWattsSensorEntity(client, self, "ratedPower", "Rated Power", False),
            
            # Voltage
            VoltSensorEntity(client, self, "carBatVolt", "Car Battery Voltage"),
            
            # Time
            RemainSensorEntity(client, self, "chargeToFull268", "Charging Time", False),
            
            # Status
            StatusSensorEntity(client, self)
        ]

    def numbers(self, client: EcoflowApiClient) -> list[NumberEntity]:
        return [
            # Start voltage (11V - 30V, step 0.1V)
            MaxBatteryLevelEntity(
                client, self, 
                "startVoltage", 
                "Start Voltage",
                11, 30,
                lambda value: {
                    "sn": self.device_info.sn,
                    "operateType": "TCP",
                    "params": {
                        "id": 17,
                        "startVoltage": int(value * 10)
                    }
                }
            ),
            
            # Power limit (0W - 800W)
            MaxBatteryLevelEntity(
                client, self,
                "permanentWatts",
                "Power Limit",
                0, 800,
                lambda value: {
                    "sn": self.device_info.sn,
                    "operateType": "TCP",
                    "params": {
                        "id": 17,
                        "permanentWatts": int(value)
                    }
                }
            ),
            
            # Cable length (0-10m)
            MinBatteryLevelEntity(
                client, self,
                "cableLength608",
                "Cable Length",
                0, 10,
                lambda value: {
                    "sn": self.device_info.sn,
                    "operateType": "TCP",
                    "params": {
                        "id": 17,
                        "cableLength608": int(value)
                    }
                }
            )
        ]

    def switches(self, client: EcoflowApiClient) -> list[SwitchEntity]:
        return [
            # Start/Stop switch
            EnabledEntity(
                client, self,
                "startStop",
                "Charger",
                lambda value: {
                    "sn": self.device_info.sn,
                    "operateType": "TCP",
                    "params": {
                        "id": 17,
                        "startStop": 1 if value else 0
                    }
                }
            )
        ]

    def selects(self, client: EcoflowApiClient) -> list[SelectEntity]:
        # Operation modes
        modes = {
            1: "Mode 1",
            2: "Mode 2",
            3: "Mode 3"
        }
        
        return [
            DictSelectEntity(
                client, self,
                "operationMode",
                "Operation Mode",
                modes,
                lambda value: {
                    "sn": self.device_info.sn,
                    "operateType": "TCP",
                    "params": {
                        "id": 17,
                        "operationMode": value
                    }
                }
            )
        ]
