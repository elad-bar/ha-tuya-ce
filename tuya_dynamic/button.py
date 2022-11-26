"""Support for Tuya buttons."""
from __future__ import annotations

from tuya_iot import TuyaDevice, TuyaDeviceManager

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .managers.tuya_device_configuration_manager import TuyaDeviceConfigurationManager
from .models.base import TuyaEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Tuya buttons dynamically through Tuya discovery."""
    manager = TuyaDeviceConfigurationManager.get_instance(hass)
    await manager.async_setup_entry(Platform.BUTTON,
                                    entry,
                                    async_add_entities,
                                    TuyaButtonEntity.create_entity)


class TuyaButtonEntity(TuyaEntity, ButtonEntity):
    """Tuya Button Device."""

    def __init__(
        self,
        device: TuyaDevice,
        device_manager: TuyaDeviceManager,
        description: ButtonEntityDescription,
    ) -> None:
        """Init Tuya button."""
        super().__init__(device, device_manager)
        self.entity_description = description
        self._attr_unique_id = f"{super().unique_id}{description.key}"

    @staticmethod
    def create_entity(device: TuyaDevice,
                      device_manager: TuyaDeviceManager,
                      description: ButtonEntityDescription):
        instance = TuyaButtonEntity(device, device_manager, description)

        return instance

    def press(self) -> None:
        """Press the button."""
        self._send_command([{"code": self.entity_description.key, "value": True}])
