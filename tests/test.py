"""Test."""
from __future__ import annotations

import asyncio
import dataclasses
import json
import logging
import os
import sys

from homeassistant.const import Platform

from ..tuya_dynamic.helpers.tuya_mapping import *

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


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)

        elif isinstance(obj, set):
            return list(obj)

        return super().default(obj)


class Test:
    """Test Class."""

    def __init__(self):
        """Do initialization of test class instance, Returns None."""

    async def initialize(self):
        """Do initialization of test dependencies instances, Returns None."""
        _LOGGER.info("Initialize")

        data_mapping = {
            Platform.CAMERA: list(CAMERAS),
            Platform.FAN: list(TUYA_SUPPORT_TYPE),
            Platform.VACUUM: list(VACUUMS),
        }

        data_items = {
            Platform.ALARM_CONTROL_PANEL: ALARM,
            Platform.BINARY_SENSOR: BINARY_SENSORS,
            Platform.BUTTON: BUTTONS,
            Platform.CLIMATE: CLIMATE_DESCRIPTIONS,
            Platform.COVER: COVERS,
            Platform.HUMIDIFIER: HUMIDIFIERS,
            Platform.LIGHT: LIGHTS,
            Platform.NUMBER: NUMBERS,
            Platform.SELECT: SELECTS,
            Platform.SENSOR: SENSORS,
            Platform.SIREN: SIRENS,
            Platform.SWITCH: SWITCHES,
        }

        devices = {}

        for domain in data_items:
            device_categories = data_items.get(domain)

            for device_category_key in device_categories:
                device_category_items = device_categories.get(device_category_key)

                if device_category_key not in devices:
                    devices[device_category_key] = {}

                devices[device_category_key][domain] = device_category_items

        for domain in data_mapping:
            device_categories = data_mapping.get(domain)

            for device_category_key in device_categories:
                if device_category_key not in devices:
                    devices[device_category_key] = {}

                devices[device_category_key][domain] = True

        """
        identical = {}
        devices_cache = {}

        for device_key in devices:
            device_data = devices[device_key]

            device_data_json = json.dumps(device_data, cls=EnhancedJSONEncoder, indent=4)

            md5 = hashlib.md5(device_data_json.encode())
            device_hash = md5.hexdigest()

            if device_hash in devices_cache:
                identical[device_hash].append(device_key)

            else:
                identical[device_hash] = [device_key]
        """

        payload = {"devices": devices}

        data = json.dumps(payload, cls=EnhancedJSONEncoder, indent=4)

        print(data)

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
