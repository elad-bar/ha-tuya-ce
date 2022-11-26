from collections.abc import Callable
import json
import logging
import sys

from tuya_iot import TuyaDeviceManager

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntityDescription,
)
from homeassistant.components.button import ButtonEntityDescription
from homeassistant.components.number import NumberEntityDescription
from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.siren import SirenEntityDescription
from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from ..helpers.const import (
    DEVICE_CONFIG_MANAGER,
    DEVICE_CONFIG_URL,
    DOMAIN,
    TUYA_DISCOVERY_NEW,
)
from ..models.color_type_data import ColorTypes
from ..models.tuya_entity_descriptors import (
    TuyaBinarySensorEntityDescription,
    TuyaClimateEntityDescription,
    TuyaCoverEntityDescription,
    TuyaHumidifierEntityDescription,
    TuyaLightEntityDescription,
    TuyaSensorEntityDescription,
)

_LOGGER = logging.getLogger(__name__)

ENTITY_DESCRIPTION_DEFAULTS = {
    "default_color_type": ColorTypes.v1,
    "open_instruction_value": "open",
    "close_instruction_value": "close",
    "stop_instruction_value": "stop",
    "on_value": True
}


class TuyaDeviceConfigurationManager:
    def __init__(self, hass):
        self._hass = hass
        self._session = async_create_clientsession(hass=self._hass)
        self._data = None
        self._domain_handlers = None

    @property
    def integration_data(self):
        return self._hass.data[DOMAIN]

    @property
    def countries(self) -> list:
        return self._data.get("countries", [])

    @property
    def device_classes(self) -> dict:
        return self._data.get("device_classes", {})

    @property
    def devices(self) -> dict:
        return self._data.get("devices", dict)

    @staticmethod
    def get_instance(hass):
        integration_data = hass.data[DOMAIN]
        instance = integration_data[DEVICE_CONFIG_MANAGER]

        return instance

    async def initialize(self):
        try:
            self._load_domain_handlers()

            if self._data is None:
                async with self._session.get(DEVICE_CONFIG_URL, ssl=False) as response:
                    response.raise_for_status()

                    content = await response.text()

                    self._data = json.loads(content)

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(f"Failed to initialize Tuya configuration manager, Error: {ex}, Line: {line_number}")

    async def async_setup_entry(self,
                                domain: str,
                                entry: ConfigEntry,
                                async_add_entities: AddEntitiesCallback,
                                initializer) -> None:

        """Set up Tuya alarm dynamically through Tuya discovery."""
        tuya_data = self.integration_data.get(entry.entry_id)
        device_manager = tuya_data.device_manager

        @callback
        def async_discover_device(device_ids: list[str]) -> None:
            """Discover and add a discovered Tuya siren."""
            entities = []

            devices_data = self._get_devices_data(entry.entry_id, domain, device_ids)

            for device_data in devices_data:
                enabled = device_data.get("enabled")
                device = device_data.get("device")
                entity_description = device_data.get("entity_description")

                _LOGGER.debug(device_data)

                if enabled:
                    try:
                        if entity_description is None:
                            instance = initializer(self._hass, device, device_manager)
                        else:
                            instance = initializer(self._hass, device, device_manager, entity_description)

                        if instance is not None:
                            entities.append(instance)
                    except Exception as ex:
                        _LOGGER.error(f"Failed to create {domain} entity, Error: {ex}")

            async_add_entities(entities)

        async_discover_device([*device_manager.device_map])

        entry.async_on_unload(
            async_dispatcher_connect(self._hass, TUYA_DISCOVERY_NEW, async_discover_device)
        )

    def _get_devices_data(self, entry_id, domain, device_ids: list[str]) -> list:
        tuya_data = self.integration_data.get(entry_id)
        device_manager = tuya_data.device_manager

        domain_handler = self._domain_handlers.get(domain)

        devices = []

        if domain_handler is None:
            _LOGGER.error(f"Tuya entity description mapper was not found for domain: {domain}")

        else:

            for device_id in device_ids:
                device = device_manager.device_map[device_id]
                category_config = self.devices.get(device.category)

                if category_config is None:
                    continue

                entities_config = category_config.get(domain)

                if entities_config is None:
                    continue

                for entity_config in entities_config:
                    mapper = domain_handler.get("mapper")
                    fields = domain_handler.get("fields")

                    device_description = mapper(entity_config, device, fields)

                    devices.append(device_description)

        return devices

    def _load_domain_handlers(self):
        self._domain_handlers = {
            Platform.CAMERA: {
                "mapper": self._mapper_camera
            },
            Platform.FAN: {
                "mapper": self._mapper_fan
            },
            Platform.VACUUM: {
                "mapper": self._mapper_vacuum
            },
            Platform.ALARM_CONTROL_PANEL: {
                "mapper": self._mapper_alarm_control_panel,
                "fields": ["name"]
            },
            Platform.BINARY_SENSOR: {
                "mapper": self._mapper_binary_sensor,
                "fields": ["dpcode", "name", "icon", "on_value", "device_class", "entity_category"]
            },
            Platform.BUTTON: {
                "mapper": self._mapper_button,
                "fields": ["name", "icon", "entity_category"]
            },
            Platform.CLIMATE: {
                "mapper": self._mapper_climate,
                "fields": ["switch_only_hvac_mode"]
            },
            Platform.COVER: {
                "mapper": self._mapper_cover,
                "fields": ["name", "current_state", "current_position", "current_position", "set_position", "device_class", "open_instruction_value", "close_instruction_value", "stop_instruction_value"]
            },
            Platform.HUMIDIFIER: {
                "mapper": self._mapper_humidifier,
                "fields": ["dpcode", "humidity", "device_class"]
            },
            Platform.LIGHT: {
                "mapper": self._mapper_light,
                "fields": ["name", "brightness", "brightness_max", "brightness_min", "device_class", "color_mode", "color_temp", "entity_category", "default_color_type", "color_data"]
            },
            Platform.NUMBER: {
                "mapper": self._mapper_number,
                "fields": ["name", "device_class", "entity_category", "icon", "native_unit_of_measurement"]
            },
            Platform.SELECT: {
                "mapper": self._mapper_select,
                "fields": ["name", "device_class", "entity_category", "icon"]
            },
            Platform.SENSOR: {
                "mapper": self._mapper_sensor,
                "fields": ["name", "device_class", "state_class", "entity_category", "icon", "native_unit_of_measurement", "entity_registry_enabled_default", "subkey"]
            },
            Platform.SIREN: {
                "mapper": self._mapper_siren,
                "fields": ["name"]
            },
            Platform.SWITCH: {
                "mapper": self._mapper_switch,
                "fields": ["name", "icon", "entity_category", "device_class"]
            },
        }

    @staticmethod
    def _mapper_camera(entity_config, device):
        data = {
            "enabled": entity_config,
            "device": device
        }

        return data

    @staticmethod
    def _mapper_fan(entity_config, device):
        data = {
            "enabled": entity_config,
            "device": device
        }

        return data

    @staticmethod
    def _mapper_vacuum(entity_config, device):
        data = {
            "enabled": entity_config,
            "device": device
        }

        return data

    @staticmethod
    def _mapper_alarm_control_panel(entity_config, device, fields: list[str]):
        entity_description = AlarmControlPanelEntityDescription(
            key=entity_config.get("key")
        )

        data = _get_entity_description(entity_description, device, entity_config, fields)

        return data

    @staticmethod
    def _mapper_binary_sensor(entity_config, device, fields: list[str]):
        entity_description = TuyaBinarySensorEntityDescription(
            key=entity_config.get("key")
        )

        validation: Callable[[EntityDescription, TuyaDeviceManager], bool] = lambda e, d: e.key in d.status or e.dpcode in d.status

        data = _get_entity_description(entity_description, device, entity_config, fields, validation)

        return data

    @staticmethod
    def _mapper_button(entity_config, device, fields: list[str]):
        entity_description = ButtonEntityDescription(
            key=entity_config.get("key")
        )

        data = _get_entity_description(entity_description, device, entity_config, fields)

        return data

    @staticmethod
    def _mapper_climate(entity_config, device, fields: list[str]):
        entity_description = TuyaClimateEntityDescription(
            key=entity_config.get("key")
        )

        data = _get_entity_description(entity_description, device, entity_config, fields)

        return data

    @staticmethod
    def _mapper_cover(entity_config, device, fields: list[str]):
        entity_description = TuyaCoverEntityDescription(
            key=entity_config.get("key")
        )

        validation: Callable[[EntityDescription, TuyaDeviceManager], bool] = lambda e, d: e.key in d.function or e.key in d.status_range

        data = _get_entity_description(entity_description, device, entity_config, fields, validation)

        return data

    @staticmethod
    def _mapper_humidifier(entity_config, device, fields: list[str]):
        entity_description = TuyaHumidifierEntityDescription(
            key=entity_config.get("key")
        )

        data = _get_entity_description(entity_description, device, entity_config, fields)

        return data

    @staticmethod
    def _mapper_light(entity_config, device, fields: list[str]):
        entity_description = TuyaLightEntityDescription(
            key=entity_config.get("key"),
        )

        data = _get_entity_description(entity_description, device, entity_config, fields)

        return data

    @staticmethod
    def _mapper_number(entity_config, device, fields: list[str]):
        entity_description = NumberEntityDescription(
            key=entity_config.get("key"),
        )

        data = _get_entity_description(entity_description, device, entity_config, fields)

        return data

    @staticmethod
    def _mapper_select(entity_config, device, fields: list[str]):
        entity_description = SelectEntityDescription(
            key=entity_config.get("key"),
        )

        data = _get_entity_description(entity_description, device, entity_config, fields)

        return data

    @staticmethod
    def _mapper_sensor(entity_config, device, fields: list[str]):
        entity_description = TuyaSensorEntityDescription(
            key=entity_config.get("key")
        )

        data = _get_entity_description(entity_description, device, entity_config, fields)

        return data

    @staticmethod
    def _mapper_siren(entity_config, device, fields: list[str]):
        entity_description = SirenEntityDescription(
            key=entity_config.get("key")
        )

        data = _get_entity_description(entity_description, device, entity_config, fields)

        return data

    @staticmethod
    def _mapper_switch(entity_config, device, fields: list[str]):
        entity_description = SwitchEntityDescription(
            key=entity_config.get("key")
        )

        data = _get_entity_description(entity_description, device, entity_config, fields)

        return data


def _get_entity_description(entity_description: EntityDescription,
                            device: TuyaDeviceManager,
                            data: dict,
                            fields: list,
                            is_enabled: Callable[[EntityDescription, TuyaDeviceManager], bool] = lambda e, d: e.key in d.status):

    for key in fields:
        value = data.get(key)

        if value is None and key in ENTITY_DESCRIPTION_DEFAULTS:
            value = ENTITY_DESCRIPTION_DEFAULTS.get(key)

        if hasattr(entity_description, key):
            setattr(entity_description, key, value)

        data = {
            "enabled": is_enabled(entity_description, device),
            "device": device,
            "entity_description": entity_description
        }

        return data
