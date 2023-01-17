"""Support for Tuya select."""
from __future__ import annotations

from tuya_iot import TuyaDevice, TuyaDeviceManager

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.components.tuya.const import DPType
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .managers.tuya_configuration_manager import TuyaConfigurationManager
from .models.base import TuyaEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Tuya select dynamically through Tuya discovery."""
    manager = TuyaConfigurationManager.get_instance(hass)
    await manager.async_setup_entry(Platform.SELECT,
                                    entry,
                                    async_add_entities,
                                    TuyaSelectEntity.create_entity)


class TuyaSelectEntity(TuyaEntity, SelectEntity):
    """Tuya Select Entity."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: TuyaDevice,
        device_manager: TuyaDeviceManager,
        description: SelectEntityDescription,
    ) -> None:
        """Init Tuya sensor."""
        super().__init__(hass, device, device_manager)
        self.entity_description = description
        self._attr_unique_id = f"{super().unique_id}{description.key}"

        self._attr_options: list[str] = []
        if enum_type := self.find_dpcode(
            description.key, dptype=DPType.ENUM, prefer_function=True
        ):
            self._attr_options = enum_type.range

    @staticmethod
    def create_entity(hass: HomeAssistant,
                      device: TuyaDevice,
                      device_manager: TuyaDeviceManager,
                      description: SelectEntityDescription):
        instance = TuyaSelectEntity(hass, device, device_manager, description)

        return instance

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        # Raw value
        value = self.device.status.get(self.entity_description.key)
        if value is None or value not in self._attr_options:
            return None

        return value

    def select_option(self, option: str) -> None:
        """Change the selected option."""
        self._send_command(
            [
                {
                    "code": self.entity_description.key,
                    "value": option,
                }
            ]
        )
