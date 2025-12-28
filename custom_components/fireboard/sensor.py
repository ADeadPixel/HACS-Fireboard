"""Platform for sensor integration."""
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfTemperature,
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS,
    UnitOfElectricPotential,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = []
    for device_uuid, device_data in coordinator.data.items():
        device_name = device_data.get("title", "FireBoard")
        
        sensors.append(FireBoardBatterySensor(coordinator, device_uuid, device_name))

        sensors.append(FireBoardVoltageSensor(coordinator, device_uuid, device_name))
        
        sensors.append(FireBoardRSSISensor(coordinator, device_uuid, device_name))

        sensors.append(FireBoardDiagnosticSensor(coordinator, device_uuid, device_name, "ssid", "SSID", None))
        sensors.append(FireBoardDiagnosticSensor(coordinator, device_uuid, device_name, "internalIP", "IP Address", None))

        for channel in device_data.get("channels", []):
            channel_id = channel.get("channel")
            channel_label = channel.get("channel_label")
            sensors.append(FireBoardProbeSensor(coordinator, device_uuid, device_name, channel_id, channel_label))

    async_add_entities(sensors)

class FireBoardBaseSensor(CoordinatorEntity):
    """Base class for FireBoard sensors."""
    def __init__(self, coordinator, device_uuid, device_name):
        super().__init__(coordinator)
        self._device_uuid = device_uuid
        self._device_name = device_name

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_uuid)},
            "name": self._device_name,
            "manufacturer": "FireBoard Labs",
            "model": self.coordinator.data[self._device_uuid].get("model", "FireBoard"),
            "sw_version": self.coordinator.data[self._device_uuid].get("version"),
        }
    
    @property
    def _device_log(self):
        """Helper to safely access the device_log dict."""
        return self.coordinator.data[self._device_uuid].get("device_log", {})

class FireBoardProbeSensor(FireBoardBaseSensor, SensorEntity):
    def __init__(self, coordinator, device_uuid, device_name, channel_id, label):
        super().__init__(coordinator, device_uuid, device_name)
        self._channel_id = channel_id
        # Use user-defined label if available, else "Channel X"
        self._attr_name = f"{device_name} {label if label else f'Channel {channel_id}'}"
        self._attr_unique_id = f"{device_uuid}_channel_{channel_id}"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    @property
    def native_value(self):
        device = self.coordinator.data.get(self._device_uuid)
        if not device: return None
        
        for ch in device.get("channels", []):
            if ch.get("channel") == self._channel_id:
                # "current_temp" is not present if probe is unplugged
                return ch.get("current_temp")
        return None

class FireBoardBatterySensor(FireBoardBaseSensor, SensorEntity):
    def __init__(self, coordinator, device_uuid, device_name):
        super().__init__(coordinator, device_uuid, device_name)
        self._attr_unique_id = f"{device_uuid}_battery"
        self._attr_name = f"{device_name} Battery"
        self._attr_device_class = SensorDeviceClass.BATTERY
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        # 'vBattPer' is 0.8728 -> 87%
        val = self._device_log.get("vBattPer")
        if val is not None:
            return int(val * 100)
        return None

class FireBoardVoltageSensor(FireBoardBaseSensor, SensorEntity):
    def __init__(self, coordinator, device_uuid, device_name):
        super().__init__(coordinator, device_uuid, device_name)
        self._attr_unique_id = f"{device_uuid}_voltage"
        self._attr_name = f"{device_name} Voltage"
        self._attr_device_class = SensorDeviceClass.VOLTAGE
        self._attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        return self._device_log.get("vBatt")

class FireBoardRSSISensor(FireBoardBaseSensor, SensorEntity):
    def __init__(self, coordinator, device_uuid, device_name):
        super().__init__(coordinator, device_uuid, device_name)
        self._attr_unique_id = f"{device_uuid}_rssi"
        self._attr_name = f"{device_name} Signal"
        self._attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
        self._attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        return self._device_log.get("signallevel")

class FireBoardDiagnosticSensor(FireBoardBaseSensor, SensorEntity):
    """Generic sensor for text-based diagnostics (SSID, IP, etc)."""
    def __init__(self, coordinator, device_uuid, device_name, key, label, icon):
        super().__init__(coordinator, device_uuid, device_name)
        self._key = key
        self._attr_unique_id = f"{device_uuid}_{key}"
        self._attr_name = f"{device_name} {label}"
        self._attr_icon = icon
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        return self._device_log.get(self._key)