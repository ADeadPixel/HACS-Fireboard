"""Platform for sensor integration."""
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfTemperature, PERCENTAGE, SIGNAL_STRENGTH_DECIBELS
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = []
    for device_uuid, device_data in coordinator.data.items():
        device_name = device_data.get("title", "FireBoard")
        
        sensors.append(FireBoardBatterySensor(coordinator, device_uuid, device_name))
        
        if "last_rssi" in device_data: 
             sensors.append(FireBoardRSSISensor(coordinator, device_uuid, device_name))

        for channel in device_data.get("channels", []):
            channel_id = channel.get("channel")
            sensors.append(FireBoardProbeSensor(coordinator, device_uuid, device_name, channel_id))

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
            "model": "FireBoard 2",
        }

class FireBoardProbeSensor(FireBoardBaseSensor, SensorEntity):
    def __init__(self, coordinator, device_uuid, device_name, channel_id):
        super().__init__(coordinator, device_uuid, device_name)
        self._channel_id = channel_id
        self._attr_unique_id = f"{device_uuid}_channel_{channel_id}"
        self._attr_name = f"{device_name} Channel {channel_id}"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS 

    @property
    def native_value(self):
        device = self.coordinator.data.get(self._device_uuid)
        if not device: return None
        
        for ch in device.get("channels", []):
            if ch.get("channel") == self._channel_id:
                return ch.get("current_temp") # Check API if it's 'temp' or 'current_temp'
        return None

class FireBoardBatterySensor(FireBoardBaseSensor, SensorEntity):
    def __init__(self, coordinator, device_uuid, device_name):
        super().__init__(coordinator, device_uuid, device_name)
        self._attr_unique_id = f"{device_uuid}_battery"
        self._attr_name = f"{device_name} Battery"
        self._attr_device_class = SensorDeviceClass.BATTERY
        self._attr_native_unit_of_measurement = PERCENTAGE

    @property
    def native_value(self):
        device = self.coordinator.data.get(self._device_uuid)
        return device.get("battery_level_percent") 

class FireBoardRSSISensor(FireBoardBaseSensor, SensorEntity):
    def __init__(self, coordinator, device_uuid, device_name):
        super().__init__(coordinator, device_uuid, device_name)
        self._attr_unique_id = f"{device_uuid}_rssi"
        self._attr_name = f"{device_name} Signal"
        self._attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
        self._attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS

    @property
    def native_value(self):
        device = self.coordinator.data.get(self._device_uuid)
        return device.get("last_rssi")