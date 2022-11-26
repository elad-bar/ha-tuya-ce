"""Support for Tuya siren."""
from __future__ import annotations

from typing import Any

from tuya_iot import TuyaDevice, TuyaDeviceManager

from homeassistant.components.siren import (
    SirenEntity,
    SirenEntityDescription,
    SirenEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .managers.tuya_device_configuration_manager import TuyaDeviceConfigurationManager
from .models.base import TuyaEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Tuya siren dynamically through Tuya discovery."""
    manager = TuyaDeviceConfigurationManager.get_instance(hass)
    await manager.async_setup_entry(Platform.SIREN,
                                    entry,
                                    async_add_entities,
                                    TuyaSirenEntity.create_entity)


class TuyaSirenEntity(TuyaEntity, SirenEntity):
    """Tuya Siren Entity."""

    _attr_supported_features = SirenEntityFeature.TURN_ON | SirenEntityFeature.TURN_OFF

    def __init__(
        self,
        hass: HomeAssistant,
        device: TuyaDevice,
        device_manager: TuyaDeviceManager,
        description: SirenEntityDescription,
    ) -> None:
        """Init Tuya Siren."""
        super().__init__(hass, device, device_manager)
        self.entity_description = description
        self._attr_unique_id = f"{super().unique_id}{description.key}"

    @staticmethod
    def create_entity(hass: HomeAssistant,
                      device: TuyaDevice,
                      device_manager: TuyaDeviceManager,
                      description: SirenEntityDescription):
        instance = TuyaSirenEntity(hass, device, device_manager, description)

        return instance

    @property
    def is_on(self) -> bool:
        """Return true if siren is on."""
        return self.device.status.get(self.entity_description.key, False)

    def turn_on(self, **kwargs: Any) -> None:
        """Turn the siren on."""
        self._send_command([{"code": self.entity_description.key, "value": True}])

    def turn_off(self, **kwargs: Any) -> None:
        """Turn the siren off."""
        self._send_command([{"code": self.entity_description.key, "value": False}])
