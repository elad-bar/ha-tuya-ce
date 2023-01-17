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
    ACCESS_MODES,
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
    TUYA_RELATED_DOMAINS,
    TUYA_SPECIAL_MAPPING,
    TUYA_TYPES_MAPPING,
    TUYA_UNSUPPORTED_CATEGORIES_DATA_KEYS,
    UNITS_CONFIG,
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
    def units(self) -> dict:
        return self._data.get(UNITS_CONFIG, {})

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
            path = f"{DOMAIN}/{config_file}.json"

            store = Store(self._hass, STORAGE_VERSION, path, encoder=JSONEncoder)

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

                    if category_config is not None:
                        platform_data = category_config.get(domain, [])

                        for platform_item in platform_data:
                            _LOGGER.debug(f"Loading domain {domain}, Details: {platform_item}")

                            is_enabled = self._platform_manager.is_enabled(domain, category_config, device)

                            if is_enabled:
                                entity_description = self._platform_manager.get_entity_description(domain, platform_item)

                                if entity_description is None:
                                    _LOGGER.debug(f"Running initializer, Domain: {domain}")
                                    instance = initializer(self._hass, device, device_manager)

                                else:
                                    _LOGGER.debug(
                                        f"Running initializer, "
                                        f"Domain: {domain}, "
                                        f"Entity_description: {entity_description}"
                                    )

                                    instance = initializer(self._hass, device, device_manager, entity_description)

                                if instance is not None:
                                    entities.append(instance)

                except Exception as ex:
                    exc_type, exc_obj, tb = sys.exc_info()
                    line_number = tb.tb_lineno

                    _LOGGER.error(f"Failed to create {domain} entity, Error: {ex}, Line: {line_number}")

            async_add_entities(entities)

        async_discover_device([*device_manager.device_map])

        entry.async_on_unload(
            async_dispatcher_connect(self._hass, TUYA_DISCOVERY_NEW, async_discover_device)
        )

    def perform_gap_analysis(self, diagnostic_data: dict):
        diagnostic_devices = diagnostic_data["devices"]

        diagnostic_devices_str = json.dumps(diagnostic_devices)
        diagnostic_devices_data = json.loads(diagnostic_devices_str)

        unsupported_devices = self._get_unsupported_categories(diagnostic_devices_data)
        _LOGGER.info(f"Unsupported devices: {json.dumps(unsupported_devices)}")

        devices = self._get_devices(diagnostic_devices_data)
        _LOGGER.info(f"Devices: {json.dumps(devices)}")

        gaps = self._get_gaps(devices)
        _LOGGER.info(f"Gaps: {json.dumps(gaps)}")

        diagnostic_data["gaps"] = gaps
        diagnostic_data["unsupported_devices"] = unsupported_devices

    def _match_components(self, gaps: dict):
        for category_key in gaps:
            category_data = gaps.get(category_key)

            for domain_key in category_data:
                domain_data = category_data.get(domain_key)

                for component_key in domain_data:
                    component = domain_data.get(component_key)

                    exiting_components = self._get_components(component_key)
                    component["matches"] = exiting_components
                    domain_data[component_key] = component

    def _get_components(self, key: str):
        components = {}
        for category_key in self.devices:
            category_data = self.devices.get(category_key, {})
            for domain_key in category_data:
                if domain_key in self._platform_manager.simple_platforms:
                    continue

                domain_data = category_data.get(domain_key)

                for domain_item in domain_data:
                    if domain_item.get("key") == key:
                        if domain_key not in components:
                            components[domain_key] = []

                        components[domain_key].append(domain_item)

        return components

    def _get_devices(self, diagnostic_devices: list) -> dict:
        result = {}
        try:
            for diagnostic_device in diagnostic_devices:
                category: str = diagnostic_device.get("category")

                functions: dict = diagnostic_device.get("function")
                status_range: dict = diagnostic_device.get("status_range")
                status: dict = diagnostic_device.get("status", {})

                category_data = result.get(category, {})

                if len(status.keys()) == 0:
                    special_mapping = TUYA_SPECIAL_MAPPING.get(category)

                    if special_mapping is not None:
                        for function in functions:
                            special_mapping_key = special_mapping.get(function, function)
                            status_range_item = status_range.get(special_mapping_key)

                            status_range_data = status_range_item
                            if status_range_data is None:
                                status_range_data = functions.get(function)

                            status_range[special_mapping_key] = status_range_data
                            status[special_mapping_key] = ""

                for status_key in status:
                    function_item = functions.get(status_key)
                    status_range_item = status_range.get(status_key)

                    is_read_only = function_item is None

                    if status_range_item is None:
                        _LOGGER.info(f"{category}.{status_key} is not supported")

                    else:
                        status_range_item_type = status_range_item.get("type")

                        key = self._get_key(is_read_only, status_range_item_type)
                        domain = TUYA_TYPES_MAPPING.get(key, "unknown")

                        domain_data = function_item

                        if isinstance(status_range_item, dict) and len(status_range_item.keys()) > 0:
                            domain_data = status_range_item

                        if "type" in domain_data:
                            type_value: str = domain_data.get("type")
                            domain_data["type"] = type_value.capitalize()

                        if "value" in domain_data:
                            value_data: str = domain_data.get("value")
                            if isinstance(value_data, str) or (isinstance(value_data, dict) and len(value_data.keys()) == 0):
                                domain_data.pop("value")

                        category_domains = category_data.get(domain, {})

                        category_domains[status_key] = domain_data

                        category_data[domain] = category_domains

                if len(category_data.keys()) > 0:
                    result[category] = category_data
        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(f"Failed to load HA data, Error: {ex}, Line: {line_number}")

        return result

    @staticmethod
    def _get_unsupported_categories(diagnostic_devices: dict):
        unsupported_categories = {}

        try:
            for diagnostic_device in diagnostic_devices:
                category: str = diagnostic_device.get("category")

                functions: dict = diagnostic_device.get("function")
                status_range: dict = diagnostic_device.get("status_range")
                status: dict = diagnostic_device.get("status", {})

                if len(status.keys()) + len(functions.keys()) + len(status_range.keys()) == 0:
                    if category not in unsupported_categories:
                        unsupported_categories[category] = []

                    unsupported_device = {}

                    for data_key in TUYA_UNSUPPORTED_CATEGORIES_DATA_KEYS:
                        unsupported_device[data_key] = diagnostic_device.get(data_key)

                    _LOGGER.debug(f"Category {category} is not supported")

                    unsupported_categories[category].append(unsupported_device)
        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(f"Failed to load HA data, Error: {ex}, Line: {line_number}")

        return unsupported_categories

    def _get_gaps(self, diagnostic_devices: dict) -> dict:
        gaps = {}
        try:
            for category_key in diagnostic_devices:
                new_category = diagnostic_devices.get(category_key)
                stored_categories = self.devices.get(category_key)

                if stored_categories is None:
                    gaps[category_key] = new_category

                    _LOGGER.debug(f"Gap identified for category {category_key}")

                else:
                    for new_device_key in new_category:
                        new_device = new_category.get(new_device_key)
                        stored_device = stored_categories.get(new_device_key)

                        if stored_device is None:
                            gaps[category_key] = {
                                new_device_key: new_device
                            }

                            _LOGGER.debug(f"Gap identified for device {category_key}.{new_device_key}")

                        else:
                            for new_domain_key in new_device:
                                new_domain = new_device.get(new_domain_key)
                                stored_domain = None

                                for stored_domain_item in stored_device:
                                    key = stored_domain_item.get("key")
                                    relevant_domains = self._get_relevant_domains(key)

                                    if key in relevant_domains:
                                        stored_domain = stored_domain_item

                                if stored_domain is None:
                                    if category_key not in gaps:
                                        gaps[category_key] = {}

                                    gaps[category_key][new_device_key] = {
                                        new_domain_key: new_domain
                                    }

                                    _LOGGER.debug(f"Gap identified for domain {category_key}.{new_device_key}.{new_domain_key}")

            self._match_components(gaps)

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(f"Failed to perform gap analysis, Error: {ex}, Line: {line_number}")

        return gaps

    @staticmethod
    async def load(hass) -> TuyaConfigurationManager:
        if DEVICE_CONFIG_MANAGER not in hass.data[DOMAIN]:
            instance = TuyaConfigurationManager(hass)
            await instance.load_configurations()

            def _update_remote_configuration(service_call):
                hass.async_create_task(instance.load_configurations(True))

            hass.services.async_register(DOMAIN,
                                         SERVICE_UPDATE_REMOTE_CONFIGURATION,
                                         _update_remote_configuration)

            hass.data[DOMAIN][DEVICE_CONFIG_MANAGER] = instance
        else:
            instance = hass.data[DOMAIN][DEVICE_CONFIG_MANAGER]

        return instance

    @staticmethod
    def _get_key(is_read_only: bool, type_str: str):
        access_mode = ACCESS_MODES[is_read_only]
        key = f"{access_mode}_{type_str.lower()}"

        return key

    @staticmethod
    def _get_relevant_domains(domain):
        domains = TUYA_RELATED_DOMAINS.get(domain, [])
        domains.append(domain)

        return domains
