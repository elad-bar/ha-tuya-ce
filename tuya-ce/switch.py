"""Support for Tuya switches."""
from __future__ import annotations

from typing import Any

from tuya_iot import TuyaDevice, TuyaDeviceManager

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .managers.tuya_device_configuration_manager import TuyaDeviceConfigurationManager
from .models.base import TuyaEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up tuya sensors dynamically through tuya discovery."""
    manager = TuyaDeviceConfigurationManager.get_instance(hass)
    await manager.async_setup_entry(Platform.SWITCH,
                                    entry,
                                    async_add_entities,
                                    TuyaSwitchEntity.create_entity)


class TuyaSwitchEntity(TuyaEntity, SwitchEntity):
    """Tuya Switch Device."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: TuyaDevice,
        device_manager: TuyaDeviceManager,
        description: SwitchEntityDescription,
    ) -> None:
        """Init TuyaHaSwitch."""
        super().__init__(hass, device, device_manager)
        self.entity_description = description
        self._attr_unique_id = f"{super().unique_id}{description.key}"

    @staticmethod
    def create_entity(hass: HomeAssistant,
                      device: TuyaDevice,
                      device_manager: TuyaDeviceManager,
                      description: SwitchEntityDescription):
        instance = TuyaSwitchEntity(hass, device, device_manager, description)

        return instance

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self.device.status.get(self.entity_description.key, False)

    def turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        self._send_command([{"code": self.entity_description.key, "value": True}])

    def turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        self._send_command([{"code": self.entity_description.key, "value": False}])
