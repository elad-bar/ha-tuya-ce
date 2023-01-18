from __future__ import annotations

from collections.abc import Callable
import logging
from typing import Any

from tuya_iot import TuyaDeviceManager

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntityDescription,
)
from homeassistant.components.button import ButtonEntityDescription
from homeassistant.components.climate import HVACMode
from homeassistant.components.number import NumberEntityDescription
from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.siren import SirenEntityDescription
from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.components.tuya.binary_sensor import (
    TuyaBinarySensorEntityDescription,
)
from homeassistant.components.tuya.climate import TuyaClimateEntityDescription
from homeassistant.components.tuya.cover import TuyaCoverEntityDescription
from homeassistant.components.tuya.humidifier import TuyaHumidifierEntityDescription
from homeassistant.components.tuya.light import TuyaLightEntityDescription
from homeassistant.components.tuya.sensor import TuyaSensorEntityDescription
from homeassistant.const import Platform
from homeassistant.helpers.entity import EntityDescription

from .. import PLATFORMS
from ..helpers.const import PLATFORM_FIELDS
from ..models.color_type_data import ColorTypes
from ..models.platform_details import PlatformDetails

_LOGGER = logging.getLogger(__name__)


class TuyaPlatformManager:
    _platform_handlers: dict[str, Callable[[dict], EntityDescription]]
    _platform_validations: dict[str, Callable[[dict | bool, TuyaDeviceManager], bool]]
    _entity_description_defaults = dict[str, Any]
    _simple_platforms: list[str]

    def __init__(self):
        self._platform_handlers = self._get_platform_handlers()
        self._platform_validations = self._get_platform_validations()
        self._default_validation = lambda e, d: e.get("key") in d.status

        self._entity_description_defaults = self._get_entity_description_defaults()
        self._simple_platforms = []

        self._set_simple_platforms()

    @property
    def simple_platforms(self) -> list[str]:
        return self._simple_platforms

    def get_platform_details(self, platform: str, category_config, device, platform_item) -> PlatformDetails:
        is_enabled = self._is_enabled(platform, category_config, device)
        is_simple = self._is_simple_platform(platform) if is_enabled else False
        entity_description = None if is_simple else self._get_entity_description(platform, platform_item)

        result = PlatformDetails(is_enabled, is_simple, entity_description)

        return result

    def _is_enabled(self,
                    platform: str,
                    data: dict,
                    device: TuyaDeviceManager) -> bool:

        result = False
        is_platform_supported = PLATFORMS.get(platform)

        if is_platform_supported:
            validation = self._platform_validations.get(platform, self._default_validation)

            result = validation(data, device)

        else:
            _LOGGER.warning(f"Platform {platform} is not supported")

        return result

    def _is_simple_platform(self, platform: str) -> bool:
        result = platform in self._simple_platforms

        return result

    def _set_simple_platforms(self):
        for platform_name in PLATFORMS:
            platform_handler = self._platform_handlers.get(platform_name)

            if platform_handler is None and platform_name not in self._simple_platforms:
                self._simple_platforms.append(platform_name)

    def _get_entity_description(self,
                                platform: str,
                                data: dict) -> EntityDescription | None:

        entity_description = None
        is_simple = self._is_simple_platform(platform)

        if is_simple is None:
            _LOGGER.warning(f"Platform {platform} configuration was not found")

        else:
            platform_handler = self._platform_handlers.get(platform)

            if platform_handler is None:
                _LOGGER.debug(f"Loading platform {platform} without entity description")

            else:
                _LOGGER.debug(f"Loading platform {platform} with entity description, Details: {data}")

                entity_description = platform_handler(data)
                platform_fields = PLATFORM_FIELDS.get(platform)

                for key in platform_fields:
                    value = data.get(key)

                    if value is None and key in self._entity_description_defaults:
                        value = self._entity_description_defaults.get(key)

                    if hasattr(entity_description, key):
                        setattr(entity_description, key, value)

        return entity_description

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

    def _get_platform_handlers(self) -> dict[str, Callable[[dict], EntityDescription]]:
        platforms = {
            Platform.ALARM_CONTROL_PANEL: self._get_alarm_control_panel_entity,
            Platform.BINARY_SENSOR: self._get_binary_sensor_entity,
            Platform.BUTTON: self._get_button_entity,
            Platform.CLIMATE: self._get_climate_entity,
            Platform.COVER: self._get_cover_entity,
            Platform.HUMIDIFIER: self._get_humidifier_entity,
            Platform.LIGHT: self._get_light_entity,
            Platform.NUMBER: self._get_number_entity,
            Platform.SELECT: self._get_select_entity,
            Platform.SENSOR: self._get_sensor_entity,
            Platform.SIREN: self._get_siren_entity,
            Platform.SWITCH: self._get_switch_entity
        }

        return platforms

    @staticmethod
    def _get_platform_validations() -> dict[str, Callable[[dict | bool, TuyaDeviceManager], bool]]:
        platforms = {
            Platform.CAMERA: lambda e, d: e,
            Platform.FAN: lambda e, d: e,
            Platform.VACUUM: lambda e, d: e,
            Platform.ALARM_CONTROL_PANEL: lambda e, d: e,
            Platform.BINARY_SENSOR: lambda e, d: e.key in d.status or e.dpcode in d.status,
            Platform.COVER: lambda e, d: e.key in d.function or e.key in d.status_range
        }

        return platforms

    @staticmethod
    def _get_alarm_control_panel_entity(entity_config: dict) -> EntityDescription:
        entity_description = AlarmControlPanelEntityDescription(
            key=entity_config.get("key")
        )

        _LOGGER.info(
            f"_get_alarm_control_panel_entity, Entity description: {entity_description}, entity: {entity_config}"
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
            key=entity_config.get("key"),
            switch_only_hvac_mode=HVACMode.OFF
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
