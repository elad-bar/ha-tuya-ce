from __future__ import annotations

import json
from json import JSONEncoder
import logging
import sys

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.storage import Store

from ..helpers.const import (
    BASE_URL,
    COUNTRIES_CONFIG,
    DEVICE_CLASS_CONFIG,
    DEVICE_CONFIG_MANAGER,
    DEVICES_CONFIG,
    DOMAIN,
    SERVICE_UPDATE_REMOTE_CONFIGURATION,
    STORAGE_VERSION,
    TUYA_CONFIGURATIONS,
    TUYA_DISCOVERY_NEW,
)
from .tuya_platform_manager import TuyaPlatformManager

_LOGGER = logging.getLogger(__name__)


class TuyaConfigurationManager:
    _stores: dict[str, Store] | None

    def __init__(self, hass):
        self._hass = hass
        self._session = async_create_clientsession(hass=self._hass)
        self._data = {}
        self._domain_handlers = None
        self._platform_manager = TuyaPlatformManager()
        self._stores = self._get_stores()

    @property
    def integration_data(self):
        return self._hass.data[DOMAIN]

    @property
    def countries(self) -> list:
        return self._data.get(COUNTRIES_CONFIG, [])

    @property
    def device_classes(self) -> dict:
        return self._data.get(DEVICE_CLASS_CONFIG, {})

    @property
    def devices(self) -> dict:
        return self._data.get(DEVICES_CONFIG, dict)

    @staticmethod
    def get_instance(hass):
        integration_data = hass.data[DOMAIN]
        instance = integration_data[DEVICE_CONFIG_MANAGER]

        return instance

    def _get_stores(self):
        stores = {}
        for config_file in TUYA_CONFIGURATIONS:
            store = Store(self._hass, STORAGE_VERSION, config_file, encoder=JSONEncoder)

            stores[config_file] = store

        return stores

    async def load_configurations(self, force_remote_config: bool = False):
        for config_file in TUYA_CONFIGURATIONS:
            store = self._stores.get(config_file)
            data = await store.async_load()

            if data is None or force_remote_config:
                data = await self._get_configuration(config_file)

                await store.async_save(data)

            self._data[config_file] = data

    async def _get_configuration(self, config_file: str) -> dict | None:
        data = None
        try:
            url = f"{BASE_URL}/{config_file}.json"
            async with self._session.get(url, ssl=False) as response:
                response.raise_for_status()

                content = await response.text()

                data = json.loads(content)

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(f"Failed to initialize Tuya configuration manager, Error: {ex}, Line: {line_number}")

        return data

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

            for device_id in device_ids:
                try:
                    device = device_manager.device_map[device_id]
                    category_config = self.devices.get(device.category)

                    is_enabled = self._platform_manager.is_enabled(domain, category_config, device)

                    if is_enabled:
                        entity_description = self._platform_manager.get_entity_description(domain, category_config)

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

    @staticmethod
    async def load(hass):
        if DEVICE_CONFIG_MANAGER not in hass.data[DOMAIN]:
            instance = TuyaConfigurationManager(hass)
            await instance.load_configurations()

            def _update_remote_configuration(service_call):
                hass.async_create_task(instance.load_configurations(True))

            hass.services.async_register(DOMAIN,
                                         SERVICE_UPDATE_REMOTE_CONFIGURATION,
                                         _update_remote_configuration)

            hass.data[DOMAIN][DEVICE_CONFIG_MANAGER] = instance
