from __future__ import annotations

import logging
from typing import Any

from tuya_iot import TuyaDeviceManager

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntityDescription,
)
from homeassistant.components.button import ButtonEntityDescription
from homeassistant.components.number import NumberEntityDescription
from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.siren import SirenEntityDescription
from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.const import Platform
from homeassistant.helpers.entity import EntityDescription
from tuya_ce.models.color_type_data import ColorTypes
from tuya_ce.models.platform_fields import PlatformFields
from tuya_ce.models.tuya_entity_descriptors import (
    TuyaBinarySensorEntityDescription,
    TuyaClimateEntityDescription,
    TuyaCoverEntityDescription,
    TuyaHumidifierEntityDescription,
    TuyaLightEntityDescription,
    TuyaSensorEntityDescription,
)
from tuya_ce.models.tuya_platform import TuyaPlatform

_LOGGER = logging.getLogger(__name__)


class TuyaPlatformManager:
    _platforms: dict[str, TuyaPlatform]
    _entity_description_defaults = dict[str, Any]

    def __init__(self):
        self._platforms = self._get_platforms()
        self._entity_description_defaults = self._get_entity_description_defaults()

    def is_enabled(self,
                   platform: str,
                   data: dict,
                   device: TuyaDeviceManager) -> bool:

        result = False
        platform_config = self._platforms.get(platform)

        if platform_config is None:
            _LOGGER.warning(f"Platform {platform} configuration was not found")

        else:
            result = platform_config.validate(data, device)

        return result

    def get_entity_description(self,
                               platform: str,
                               data: dict) -> EntityDescription | None:

        result = None
        platform_config = self._platforms.get(platform)

        if platform_config is None:
            _LOGGER.warning(f"Platform {platform} configuration was not found")

        else:
            if platform_config.get_entity_description is not None:
                entity_description = platform_config.get_entity_description(data)

                for key in platform_config.fields:
                    value = data.get(key)

                    if value is None and key in self._entity_description_defaults:
                        value = self._entity_description_defaults.get(key)

                    if hasattr(entity_description, key):
                        setattr(entity_description, key, value)

        return result

    @staticmethod
    def _get_entity_description_defaults() -> dict[str, Any]:
        entity_description_defaults = {
            "default_color_type": ColorTypes.v1,
            "open_instruction_value": "open",
            "close_instruction_value": "close",
            "stop_instruction_value": "stop",
            "on_value": True
        }

        return entity_description_defaults

    def _get_platforms(self):
        platforms = {
            Platform.CAMERA: TuyaPlatform(
                name=Platform.CAMERA,
                validate=lambda e, d: e
            ),
            Platform.FAN: TuyaPlatform(
                name=Platform.CAMERA,
                validate=lambda e, d: e
            ),
            Platform.VACUUM: TuyaPlatform(
                name=Platform.CAMERA,
                validate=lambda e, d: e
            ),
            Platform.ALARM_CONTROL_PANEL: TuyaPlatform(
                name=Platform.ALARM_CONTROL_PANEL,
                validate=lambda e, d: e,
                get_entity_description=self._get_alarm_control_panel_entity,
                fields=PlatformFields.ALARM_CONTROL_PANEL
            ),
            Platform.BINARY_SENSOR: TuyaPlatform(
                name=Platform.BINARY_SENSOR,
                validate=lambda e, d: e.key in d.status or e.dpcode in d.status,
                get_entity_description=self._get_binary_sensor_entity,
                fields=PlatformFields.BINARY_SENSOR
            ),
            Platform.BUTTON: TuyaPlatform(
                name=Platform.BUTTON,
                get_entity_description=self._get_button_entity,
                fields=PlatformFields.BUTTON
            ),
            Platform.CLIMATE: TuyaPlatform(
                name=Platform.CLIMATE,
                get_entity_description=self._get_climate_entity,
                fields=PlatformFields.CLIMATE
            ),
            Platform.COVER: TuyaPlatform(
                name=Platform.COVER,
                get_entity_description=self._get_cover_entity,
                fields=PlatformFields.COVER,
                validate=lambda e, d: e.key in d.function or e.key in d.status_range
            ),
            Platform.HUMIDIFIER: TuyaPlatform(
                name=Platform.HUMIDIFIER,
                get_entity_description=self._get_humidifier_entity,
                fields=PlatformFields.HUMIDIFIER
            ),
            Platform.LIGHT: TuyaPlatform(
                name=Platform.LIGHT,
                get_entity_description=self._get_light_entity,
                fields=PlatformFields.LIGHT
            ),
            Platform.NUMBER: TuyaPlatform(
                name=Platform.NUMBER,
                get_entity_description=self._get_number_entity,
                fields=PlatformFields.NUMBER
            ),
            Platform.SELECT: TuyaPlatform(
                name=Platform.SELECT,
                get_entity_description=self._get_select_entity,
                fields=PlatformFields.SELECT
            ),
            Platform.SENSOR: TuyaPlatform(
                name=Platform.SENSOR,
                get_entity_description=self._get_sensor_entity,
                fields=PlatformFields.SENSOR
            ),
            Platform.SIREN: TuyaPlatform(
                name=Platform.SIREN,
                get_entity_description=self._get_siren_entity,
                fields=PlatformFields.SIREN
            ),
            Platform.SWITCH: TuyaPlatform(
                name=Platform.SWITCH,
                get_entity_description=self._get_switch_entity,
                fields=PlatformFields.SWITCH
            ),
        }

        return platforms

    @staticmethod
    def _get_alarm_control_panel_entity(entity_config: dict) -> EntityDescription:
        entity_description = AlarmControlPanelEntityDescription(
            key=entity_config.get("key")
        )

        return entity_description

    @staticmethod
    def _get_binary_sensor_entity(entity_config: dict) -> EntityDescription:
        entity_description = TuyaBinarySensorEntityDescription(
            key=entity_config.get("key")
        )

        return entity_description

    @staticmethod
    def _get_button_entity(entity_config: dict) -> EntityDescription:
        entity_description = ButtonEntityDescription(
            key=entity_config.get("key")
        )

        return entity_description

    @staticmethod
    def _get_climate_entity(entity_config: dict) -> EntityDescription:
        entity_description = TuyaClimateEntityDescription(
            key=entity_config.get("key")
        )

        return entity_description

    @staticmethod
    def _get_cover_entity(entity_config: dict) -> EntityDescription:
        entity_description = TuyaCoverEntityDescription(
            key=entity_config.get("key")
        )

        return entity_description

    @staticmethod
    def _get_humidifier_entity(entity_config: dict) -> EntityDescription:
        entity_description = TuyaHumidifierEntityDescription(
            key=entity_config.get("key")
        )

        return entity_description

    @staticmethod
    def _get_light_entity(entity_config: dict) -> EntityDescription:
        entity_description = TuyaLightEntityDescription(
            key=entity_config.get("key")
        )

        return entity_description

    @staticmethod
    def _get_number_entity(entity_config: dict) -> EntityDescription:
        entity_description = NumberEntityDescription(
            key=entity_config.get("key")
        )

        return entity_description

    @staticmethod
    def _get_select_entity(entity_config: dict) -> EntityDescription:
        entity_description = SelectEntityDescription(
            key=entity_config.get("key")
        )

        return entity_description

    @staticmethod
    def _get_sensor_entity(entity_config: dict) -> EntityDescription:
        entity_description = TuyaSensorEntityDescription(
            key=entity_config.get("key")
        )

        return entity_description

    @staticmethod
    def _get_siren_entity(entity_config: dict) -> EntityDescription:
        entity_description = SirenEntityDescription(
            key=entity_config.get("key")
        )

        return entity_description

    @staticmethod
    def _get_switch_entity(entity_config: dict) -> EntityDescription:
        entity_description = SwitchEntityDescription(
            key=entity_config.get("key")
        )

        return entity_description
