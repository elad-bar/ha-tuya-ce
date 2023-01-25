"""HA's mapper."""
from __future__ import annotations

import json
import logging
import os
import sys

from custom_components.tuya_ce.helpers.const import *

_LOGGER = logging.getLogger(__name__)


class HAMapper:
    def __init__(self):
        self._data = {}

        self._complex_platforms = [
            Platform.ALARM_CONTROL_PANEL,
            Platform.BINARY_SENSOR,
            Platform.BUTTON,
            Platform.CLIMATE,
            Platform.COVER,
            Platform.HUMIDIFIER,
            Platform.LIGHT,
            Platform.NUMBER,
            Platform.SELECT,
            Platform.SENSOR,
            Platform.SIREN,
            Platform.SWITCH
        ]

    @property
    def countries(self) -> list:
        return self._data.get(COUNTRIES_CONFIG, [])

    @property
    def units(self) -> dict:
        return self._data.get(UNITS_CONFIG, {})

    @property
    def devices(self) -> dict:
        return self._data.get(DEVICES_CONFIG, dict)

    async def gap_analysis(self, data):
        await self.load_configurations()

        result = self.perform_device_gap_analysis(data)

        return result

    def _get_data(self, file):
        path = os.path.relpath(f"../config/{file}.json")
        with open(path) as f:
            content = f.read()

        data = json.loads(content)

        return data

    async def load_configurations(self, force_remote_config: bool = False):
        for config_file in TUYA_CONFIGURATIONS:
            self._data[config_file] = self._get_data(config_file)

    def perform_device_gap_analysis(self, diagnostic_device_data: dict):
        unsupported_devices = self._get_device_unsupported_categories(diagnostic_device_data)
        _LOGGER.info(f"Unsupported devices: {json.dumps(unsupported_devices)}")

        devices = self._get_device(diagnostic_device_data)
        _LOGGER.info(f"Devices: {json.dumps(devices)}")

        gaps = self._get_gaps(devices)
        _LOGGER.info(f"Gaps: {json.dumps(gaps)}")

        result = {
            "device": diagnostic_device_data,
            "gaps": gaps,
            "unsupported_devices": unsupported_devices
        }

        return result

    def _get_device(self, diagnostic_device: dict) -> dict:
        category_data = {}
        try:
            category: str = diagnostic_device.get("category")

            functions: dict = diagnostic_device.get("function")
            status_range: dict = diagnostic_device.get("status_range")
            status: dict = diagnostic_device.get("status", {})

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

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(f"Failed to load HA data, Error: {ex}, Line: {line_number}")

        return category_data

    @staticmethod
    def _get_device_unsupported_categories(diagnostic_device: dict):
        unsupported_categories = {}

        try:
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

            # self._match_components(gaps)

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(f"Failed to perform gap analysis, Error: {ex}, Line: {line_number}")

        return gaps

    def _match_components(self, gaps: dict):
        try:

            for category_key in gaps:
                category_data = gaps.get(category_key)

                for domain_key in category_data:
                    domain_data = category_data.get(domain_key)

                    for component_key in domain_data:
                        component = domain_data.get(component_key)

                        exiting_components = self._get_components(component_key)
                        component["matches"] = exiting_components
                        domain_data[component_key] = component

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(f"Failed to perform gap analysis, Error: {ex}, Line: {line_number}")

    def _get_components(self, key: str):
        components = {}
        for category_key in self.devices:
            category_data = self.devices.get(category_key, {})
            for domain_key in category_data:
                if domain_key not in self._complex_platforms:
                    continue

                domain_data = category_data.get(domain_key)

                for domain_item in domain_data:
                    if domain_item.get("key") == key:
                        if domain_key not in components:
                            components[domain_key] = []

                        components[domain_key].append(domain_item)

        return components

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
