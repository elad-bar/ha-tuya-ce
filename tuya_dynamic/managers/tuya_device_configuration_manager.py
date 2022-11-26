import json
import logging
import sys

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
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from tuya_dynamic import (
    DEVICE_CONFIG_MANAGER,
    DEVICE_CONFIG_URL,
    DOMAIN,
    TUYA_DISCOVERY_NEW,
)
from tuya_dynamic.binary_sensor import TuyaBinarySensorEntityDescription
from tuya_dynamic.models.tuya_entity_descriptors import (
    TuyaClimateEntityDescription,
    TuyaCoverEntityDescription,
    TuyaHumidifierEntityDescription,
    TuyaLightEntityDescription,
    TuyaSensorEntityDescription,
)

_LOGGER = logging.getLogger(__name__)


class TuyaDeviceConfigurationManager:
    def __init__(self, hass):
        self._hass = hass
        self._session = async_create_clientsession(hass=self._hass)
        self._data = None
        self._mappers = None

    @property
    def integration_data(self):
        return self._hass.data[DOMAIN]

    @staticmethod
    def get_instance(hass):
        integration_data = hass.data[DOMAIN]
        instance = integration_data[DEVICE_CONFIG_MANAGER]

        return instance

    async def initialize(self):
        try:
            self._load_mappers()

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

                if enabled:
                    if entity_description is None:
                        instance = initializer(device, device_manager)
                    else:
                        instance = initializer(device, device_manager, entity_description)

                    if instance is not None:
                        entities.append(instance)

            async_add_entities(entities)

        async_discover_device([*device_manager.device_map])

        entry.async_on_unload(
            async_dispatcher_connect(self._hass, TUYA_DISCOVERY_NEW, async_discover_device)
        )

    def _get_devices_data(self, entry_id, domain, device_ids: list[str]) -> list:
        tuya_data = self.integration_data.get(entry_id)
        device_manager = tuya_data.device_manager

        mapper = self._mappers.get(domain)

        devices = []

        if mapper is None:
            _LOGGER.error(f"Tuya entity description mapper was not found for domain: {domain}")

        else:

            for device_id in device_ids:
                device = device_manager.device_map[device_id]
                category_config = self._data.get(device.category)

                if category_config is None:
                    continue

                entities_config = category_config.get(domain)

                if entities_config is None:
                    continue

                for entity_config in entities_config:
                    device_description = mapper(entity_config, device)

                    devices.append(device_description)

        return devices

    def _load_mappers(self):
        self._mappers = {
            Platform.CAMERA: self._mapper_camera,
            Platform.FAN: self._mapper_fan,
            Platform.VACUUM: self._mapper_vacuum,
            Platform.ALARM_CONTROL_PANEL: self._mapper_alarm_control_panel,
            Platform.BINARY_SENSOR: self._mapper_binary_sensor,
            Platform.BUTTON: self._mapper_button,
            Platform.CLIMATE: self._mapper_climate,
            Platform.COVER: self._mapper_cover,
            Platform.HUMIDIFIER: self._mapper_humidifier,
            Platform.LIGHT: self._mapper_light,
            Platform.NUMBER: self._mapper_number,
            Platform.SELECT: self._mapper_select,
            Platform.SENSOR: self._mapper_sensor,
            Platform.SIREN: self._mapper_siren,
            Platform.SWITCH: self._mapper_switch
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
    def _mapper_alarm_control_panel(entity_config, device):
        entity_description = AlarmControlPanelEntityDescription(
            key=entity_config.get("key"),
            name=entity_config.get("name")
        )

        data = {
            "enabled": entity_description.key in device.status,
            "device": device,
            "entity_description": entity_description
        }

        return data

    @staticmethod
    def _mapper_binary_sensor(entity_config, device):
        entity_description = TuyaBinarySensorEntityDescription(
            key=entity_config.get("key"),
            dpcode=entity_config.get("dpcode"),
            name=entity_config.get("name"),
            icon=entity_config.get("icon"),
            on_value=entity_config.get("on_value"),
            device_class=entity_config.get("device_class"),
            entity_category=entity_config.get("entity_category"),
        )

        dpcode = entity_description.dpcode or entity_description.key

        data = {
            "enabled": dpcode in device.status,
            "device": device,
            "entity_description": entity_description
        }

        return data

    @staticmethod
    def _mapper_button(entity_config, device):
        entity_description = ButtonEntityDescription(
            key=entity_config.get("key"),
            name=entity_config.get("name"),
            icon=entity_config.get("icon"),
            entity_category=entity_config.get("entity_category"),
        )

        data = {
            "enabled": entity_description.key in device.status,
            "device": device,
            "entity_description": entity_description
        }

        return data

    @staticmethod
    def _mapper_climate(entity_config, device):
        entity_description = TuyaClimateEntityDescription(
            key=entity_config.get("key"),
            switch_only_hvac_mode=entity_config.get("switch_only_hvac_mode"),
        )

        data = {
            "enabled": entity_description.key in device.status,
            "device": device,
            "entity_description": entity_description
        }

        return data

    @staticmethod
    def _mapper_cover(entity_config, device):
        entity_description = TuyaCoverEntityDescription(
            key=entity_config.get("key"),
            name=entity_config.get("name"),
            current_state=entity_config.get("current_state"),
            current_position=entity_config.get("current_position"),
            set_position=entity_config.get("set_position"),
            device_class=entity_config.get("device_class"),
            open_instruction_value=entity_config.get("open_instruction_value"),
            close_instruction_value=entity_config.get("close_instruction_value"),
            stop_instruction_value=entity_config.get("stop_instruction_value"),
        )

        entity_key = entity_description.key

        data = {
            "enabled": entity_key in device.function or entity_key in device.status_range,
            "device": device,
            "entity_description": entity_description
        }

        return data

    @staticmethod
    def _mapper_humidifier(entity_config, device):
        entity_description = TuyaHumidifierEntityDescription(
            key=entity_config.get("key"),
            dpcode=entity_config.get("dpcode"),
            humidity=entity_config.get("humidity"),
            device_class=entity_config.get("device_class"),
        )

        data = {
            "enabled": entity_description.key in device.status,
            "device": device,
            "entity_description": entity_description
        }

        return data

    @staticmethod
    def _mapper_light(entity_config, device):
        entity_description = TuyaLightEntityDescription(
            key=entity_config.get("key"),
            name=entity_config.get("name"),
            brightness=entity_config.get("brightness"),
            brightness_max=entity_config.get("brightness_max"),
            brightness_min=entity_config.get("brightness_min"),
            device_class=entity_config.get("device_class"),
            color_mode=entity_config.get("color_mode"),
            color_temp=entity_config.get("color_temp"),
            entity_category=entity_config.get("entity_category"),
            default_color_type=entity_config.get("default_color_type"),
            color_data=entity_config.get("color_data"),
        )

        data = {
            "enabled": entity_description.key in device.status,
            "device": device,
            "entity_description": entity_description
        }

        return data

    @staticmethod
    def _mapper_number(entity_config, device):
        entity_description = NumberEntityDescription(
            key=entity_config.get("key"),
            name=entity_config.get("name"),
            device_class=entity_config.get("device_class"),
            entity_category=entity_config.get("entity_category"),
            icon=entity_config.get("icon"),
            native_unit_of_measurement=entity_config.get("native_unit_of_measurement")
        )

        data = {
            "enabled": entity_description.key in device.status,
            "device": device,
            "entity_description": entity_description
        }

        return data

    @staticmethod
    def _mapper_select(entity_config, device):
        entity_description = SelectEntityDescription(
            key=entity_config.get("key"),
            name=entity_config.get("name"),
            device_class=entity_config.get("device_class"),
            entity_category=entity_config.get("entity_category"),
            icon=entity_config.get("icon"),
        )

        data = {
            "enabled": entity_description.key in device.status,
            "device": device,
            "entity_description": entity_description
        }

        return data

    @staticmethod
    def _mapper_sensor(entity_config, device):
        entity_description = TuyaSensorEntityDescription(
            key=entity_config.get("key"),
            name=entity_config.get("name"),
            device_class=entity_config.get("device_class"),
            state_class=entity_config.get("state_class"),
            entity_category=entity_config.get("entity_category"),
            icon=entity_config.get("icon"),
            native_unit_of_measurement=entity_config.get("native_unit_of_measurement"),
            entity_registry_enabled_default=entity_config.get("entity_registry_enabled_default"),
            subkey=entity_config.get("subkey"),
        )

        data = {
            "enabled": entity_description.key in device.status,
            "device": device,
            "entity_description": entity_description
        }

        return data

    @staticmethod
    def _mapper_siren(entity_config, device):
        entity_description = SirenEntityDescription(
            key=entity_config.get("key"),
            name=entity_config.get("name"),
        )

        data = {
            "enabled": entity_description.key in device.status,
            "device": device,
            "entity_description": entity_description
        }

        return data

    @staticmethod
    def _mapper_switch(entity_config, device):
        entity_description = SwitchEntityDescription(
            key=entity_config.get("key"),
            name=entity_config.get("name"),
            icon=entity_config.get("icon"),
            entity_category=entity_config.get("entity_category"),
            device_class=entity_config.get("device_class"),
        )

        data = {
            "enabled": entity_description.key in device.status,
            "device": device,
            "entity_description": entity_description
        }

        return data
