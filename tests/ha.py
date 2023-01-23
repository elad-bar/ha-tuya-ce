import asyncio
import json
import logging
import os
import sys

from custom_components.tuya_ce import (
    TUYA_RELATED_DOMAINS,
    TUYA_SPECIAL_MAPPING,
    TUYA_TYPES_MAPPING,
)

DEBUG = str(os.environ.get("DEBUG", False)).lower() == str(True).lower()

log_level = logging.DEBUG if DEBUG else logging.INFO

root = logging.getLogger()
root.setLevel(log_level)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(log_level)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
stream_handler.setFormatter(formatter)
root.addHandler(stream_handler)

_LOGGER = logging.getLogger(__name__)


class Test:
    """Test Class."""

    def __init__(self):
        """Do initialization of test class instance, Returns None."""

        self._ignore_platforms = []

        self._data_gaps = {}

        self._ha_data = {}
        self._existing_data = self._get_data("devices")

        data = self._get_data("ha")
        tuya_data = data.get("data")
        self._diagnostic_data = tuya_data.get("devices")

        self._unsupported_categories = {}

        self._countries = self._get_data("countries")

    @staticmethod
    def _get_key(is_read_only: bool, type_str: str):
        key = f"{is_read_only}_{type_str.lower()}"

        return key

    def _get_relevant_domains(self, domain):
        domains = TUYA_RELATED_DOMAINS.get(domain, [])
        domains.append(domain)

        return domains

    def _get_data(self, file):
        path = os.path.relpath(f"../config/{file}.json")
        with open(path) as f:
            content = f.read()

        data = json.loads(content)

        return data

    def _match_components(self):
        component = None
        for category_key in self._data_gaps:
            category_data = self._data_gaps.get(category_key)

            for domain_key in category_data:
                domain_data = category_data.get(domain_key)

                for component_key in domain_data:
                    component = domain_data.get(component_key)

                    exiting_components = self._get_components(component_key)
                    component["matches"] = exiting_components
                    domain_data[component_key] = component

        return component

    def _get_components(self, key):
        components = {}
        for category_key in self._existing_data:
            category_data = self._existing_data.get(category_key, {})
            for domain_key in category_data:
                if domain_key in self._ignore_platforms:
                    continue

                domain_data = category_data.get(domain_key)

                for domain_item in domain_data:
                    if domain_item.get("key") == key:
                        if domain_key not in components:
                            components[domain_key] = []

                        components[domain_key].append(domain_item)

        return components

    def _load_ha_data(self):
        try:
            for device_data in self._diagnostic_data:
                category = device_data.get("category")

                functions: dict = device_data.get("function")
                status_range: dict = device_data.get("status_range")
                status: dict = device_data.get("status")

                # _LOGGER.info(f"Category: {category} [{name} | {model} | {product_name}]")
                category_data = self._ha_data.get(category, {})

                if len(status.keys()) == 0:
                    special_mapping = TUYA_SPECIAL_MAPPING.get(category)

                    if special_mapping is not None:
                        for function in functions:
                            special_mapping_key = special_mapping.get(
                                function, function
                            )
                            status_range_item = status_range.get(special_mapping_key)

                            status[special_mapping_key] = ""
                            status_range[special_mapping_key] = (
                                functions.get(function)
                                if status_range_item is None
                                else status_range_item
                            )

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

                        if domain == "unknown":
                            print(f"Unknown category {category}")

                        domain_items = category_data.get(domain, {})

                        domain_data = function_item

                        if (
                            isinstance(status_range_item, dict)
                            and len(status_range_item.keys()) > 0
                        ):
                            domain_data = status_range_item

                        if "type" in domain_data:
                            type_value: str = domain_data.get("type")
                            domain_data["type"] = type_value.capitalize()

                        if "value" in domain_data:
                            value_data: str = domain_data.get("value")
                            if isinstance(value_data, str) or (
                                isinstance(value_data, dict)
                                and len(value_data.keys()) == 0
                            ):
                                domain_data.pop("value")

                        domain_items[status_key] = domain_data

                        category_data[domain] = domain_items

                if len(category_data.keys()) > 0:
                    self._ha_data[category] = category_data

                else:
                    if category not in self._unsupported_categories:
                        self._unsupported_categories[category] = []

                    data_keys = ["name", "model", "product_name"]

                    unsupported_device = {}
                    for data_key in data_keys:
                        unsupported_device[data_key] = device_data.get(data_key)

                    self._unsupported_categories[category].append(unsupported_device)
        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(f"Failed to load HA data, Error: {ex}, Line: {line_number}")

    def _gap_analysis(self):
        try:
            for category_key in self._ha_data:
                _LOGGER.debug(f"category_key: {category_key}")
                new_category = self._ha_data.get(category_key)
                stored_categories = self._existing_data.get(category_key)

                if stored_categories is None:
                    self._data_gaps[category_key] = new_category

                    _LOGGER.debug(f"category_key: {category_key}: {new_category} ")

                else:
                    for new_device_key in new_category:
                        new_device = new_category.get(new_device_key)
                        stored_device = stored_categories.get(new_device_key)

                        _LOGGER.debug(
                            f"new_domain_key: {category_key}.{new_device_key}: {new_device} "
                        )

                        if stored_device is None:
                            self._data_gaps[category_key] = {new_device_key: new_device}

                        else:
                            for new_domain_key in new_device:
                                new_domain = new_device.get(new_domain_key)
                                stored_domain = None

                                for stored_domain_item in stored_device:
                                    key = stored_domain_item.get("key")
                                    relevant_domains = self._get_relevant_domains(key)

                                    if key in relevant_domains:
                                        stored_domain = stored_domain_item

                                _LOGGER.debug(
                                    f"new_domain_key: {category_key}.{new_device_key}.{new_domain_key}: {list(new_device.keys())} |>>> {stored_device}"
                                )

                                if stored_domain is None:
                                    if category_key not in self._data_gaps:
                                        self._data_gaps[category_key] = {}

                                    self._data_gaps[category_key][new_device_key] = {
                                        new_domain_key: new_domain
                                    }
        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(
                f"Failed to perform gap analysis, Error: {ex}, Line: {line_number}"
            )

    def _log_data(self, title, data):
        data_json = json.dumps(data, indent=4)

        _LOGGER.info(f"{title}: {data_json}")

    async def initialize(self):
        """Do initialization of test dependencies instances, Returns None."""
        _LOGGER.info("Initialize")
        """
        self._load_ha_data()
        self._gap_analysis()
        self._match_components()

        self._log_data("Unsupported categories", self._unsupported_categories)
        self._log_data("Gaps", self._data_gaps)
        """

    async def terminate(self):
        """Do termination of API, Returns None."""
        _LOGGER.info("Terminate")


instance = Test()
loop = asyncio.new_event_loop()

try:
    loop.run_until_complete(instance.initialize())

except KeyboardInterrupt:
    _LOGGER.info("Aborted")
    loop.run_until_complete(instance.terminate())

except Exception as rex:
    _LOGGER.error(f"Error: {rex}")
