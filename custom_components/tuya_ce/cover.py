"""Support for Tuya Cover."""
from __future__ import annotations

from typing import Any

from tuya_iot import TuyaDevice, TuyaDeviceManager

from homeassistant.components.cover import (
    ATTR_POSITION,
    ATTR_TILT_POSITION,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.components.tuya.const import DPCode, DPType
from homeassistant.components.tuya.cover import TuyaCoverEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .managers.tuya_configuration_manager import TuyaConfigurationManager
from .models.base import IntegerTypeData, TuyaEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Tuya cover dynamically through Tuya discovery."""
    manager = TuyaConfigurationManager.get_instance(hass)
    await manager.async_setup_entry(Platform.COVER,
                                    entry,
                                    async_add_entities,
                                    TuyaCoverEntity.create_entity)


class TuyaCoverEntity(TuyaEntity, CoverEntity):
    """Tuya Cover Device."""

    _current_position: IntegerTypeData | None = None
    _set_position: IntegerTypeData | None = None
    _tilt: IntegerTypeData | None = None
    entity_description: TuyaCoverEntityDescription

    def __init__(
        self,
        hass: HomeAssistant,
        device: TuyaDevice,
        device_manager: TuyaDeviceManager,
        description: TuyaCoverEntityDescription,
    ) -> None:
        """Init Tuya Cover."""
        super().__init__(hass, device, device_manager)
        self.entity_description = description
        self._attr_unique_id = f"{super().unique_id}{description.key}"
        self._attr_supported_features = CoverEntityFeature(0)

        # Check if this cover is based on a switch or has controls
        if self.find_dpcode(description.key, prefer_function=True):
            if device.function[description.key].type == "Boolean":
                self._attr_supported_features |= (
                    CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE
                )
            elif enum_type := self.find_dpcode(
                description.key, dptype=DPType.ENUM, prefer_function=True
            ):
                if description.open_instruction_value in enum_type.range:
                    self._attr_supported_features |= CoverEntityFeature.OPEN
                if description.close_instruction_value in enum_type.range:
                    self._attr_supported_features |= CoverEntityFeature.CLOSE
                if description.stop_instruction_value in enum_type.range:
                    self._attr_supported_features |= CoverEntityFeature.STOP

        # Determine type to use for setting the position
        if int_type := self.find_dpcode(
            description.set_position, dptype=DPType.INTEGER, prefer_function=True
        ):
            self._attr_supported_features |= CoverEntityFeature.SET_POSITION
            self._set_position = int_type
            # Set as default, unless overwritten below
            self._current_position = int_type

        # Determine type for getting the position
        if int_type := self.find_dpcode(
            description.current_position, dptype=DPType.INTEGER, prefer_function=True
        ):
            self._current_position = int_type

        # Determine type to use for setting the tilt
        if int_type := self.find_dpcode(
            (DPCode.ANGLE_HORIZONTAL, DPCode.ANGLE_VERTICAL),
            dptype=DPType.INTEGER,
            prefer_function=True,
        ):
            self._attr_supported_features |= CoverEntityFeature.SET_TILT_POSITION
            self._tilt = int_type

    @staticmethod
    def create_entity(hass: HomeAssistant,
                      device: TuyaDevice,
                      device_manager: TuyaDeviceManager,
                      description: TuyaCoverEntityDescription):
        instance = TuyaCoverEntity(hass, device, device_manager, description)

        return instance

    @property
    def current_cover_position(self) -> int | None:
        """Return cover current position."""
        if self._current_position is None:
            return None

        if (position := self.device.status.get(self._current_position.dpcode)) is None:
            return None

        return round(
            self._current_position.remap_value_to(position, 0, 100, reverse=True)
        )

    @property
    def current_cover_tilt_position(self) -> int | None:
        """Return current position of cover tilt.

        None is unknown, 0 is closed, 100 is fully open.
        """
        if self._tilt is None:
            return None

        if (angle := self.device.status.get(self._tilt.dpcode)) is None:
            return None

        return round(self._tilt.remap_value_to(angle, 0, 100))

    @property
    def is_closed(self) -> bool | None:
        """Return true if cover is closed."""
        if (
            self.entity_description.current_state is not None
            and (
                current_state := self.device.status.get(
                    self.entity_description.current_state
                )
            )
            is not None
        ):
            return self.entity_description.current_state_inverse is not (
                current_state in (True, "fully_close")
            )

        if (position := self.current_cover_position) is not None:
            return position == 0

        return None

    def open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        value: bool | str = True
        if self.find_dpcode(
            self.entity_description.key, dptype=DPType.ENUM, prefer_function=True
        ):
            value = self.entity_description.open_instruction_value

        commands: list[dict[str, str | int]] = [
            {"code": self.entity_description.key, "value": value}
        ]

        if self._set_position is not None:
            commands.append(
                {
                    "code": self._set_position.dpcode,
                    "value": round(
                        self._set_position.remap_value_from(100, 0, 100, reverse=True),
                    ),
                }
            )

        self._send_command(commands)

    def close_cover(self, **kwargs: Any) -> None:
        """Close cover."""
        value: bool | str = False
        if self.find_dpcode(
            self.entity_description.key, dptype=DPType.ENUM, prefer_function=True
        ):
            value = self.entity_description.close_instruction_value

        commands: list[dict[str, str | int]] = [
            {"code": self.entity_description.key, "value": value}
        ]

        if self._set_position is not None:
            commands.append(
                {
                    "code": self._set_position.dpcode,
                    "value": round(
                        self._set_position.remap_value_from(0, 0, 100, reverse=True),
                    ),
                }
            )

        self._send_command(commands)

    def set_cover_position(self, **kwargs: Any) -> None:
        """Move the cover to a specific position."""
        if self._set_position is None:
            raise RuntimeError(
                "Cannot set position, device doesn't provide methods to set it"
            )

        self._send_command(
            [
                {
                    "code": self._set_position.dpcode,
                    "value": round(
                        self._set_position.remap_value_from(
                            kwargs[ATTR_POSITION], 0, 100, reverse=True
                        )
                    ),
                }
            ]
        )

    def stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        self._send_command(
            [
                {
                    "code": self.entity_description.key,
                    "value": self.entity_description.stop_instruction_value,
                }
            ]
        )

    def set_cover_tilt_position(self, **kwargs: Any) -> None:
        """Move the cover tilt to a specific position."""
        if self._tilt is None:
            raise RuntimeError(
                "Cannot set tilt, device doesn't provide methods to set it"
            )

        self._send_command(
            [
                {
                    "code": self._tilt.dpcode,
                    "value": round(
                        self._tilt.remap_value_from(
                            kwargs[ATTR_TILT_POSITION], 0, 100, reverse=True
                        )
                    ),
                }
            ]
        )
