"""Device's mapper."""
from __future__ import annotations

import json
import logging

from custom_components.tuya_ce.helpers.const import (
    ELECTRIC_RESISTANCE_OHM,
    PLATFORM_FIELDS,
    WEATHER_CONDITION,
)
from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.components.tuya.alarm_control_panel import ALARM
from homeassistant.components.tuya.binary_sensor import BINARY_SENSORS
from homeassistant.components.tuya.button import BUTTONS
from homeassistant.components.tuya.camera import CAMERAS
from homeassistant.components.tuya.climate import CLIMATE_DESCRIPTIONS
from homeassistant.components.tuya.cover import COVERS
from homeassistant.components.tuya.fan import TUYA_SUPPORT_TYPE
from homeassistant.components.tuya.humidifier import HUMIDIFIERS
from homeassistant.components.tuya.light import LIGHTS
from homeassistant.components.tuya.number import NUMBERS
from homeassistant.components.tuya.select import SELECTS
from homeassistant.components.tuya.sensor import SENSORS, TuyaSensorEntityDescription
from homeassistant.components.tuya.siren import SIRENS
from homeassistant.components.tuya.switch import SWITCHES
from homeassistant.const import Platform, UnitOfMass

from ..helpers.dp_code import ExtendedDPCode
from ..helpers.enhanced_json_encoder import EnhancedJSONEncoder
from ..helpers.tuya_mapping import VACUUMS
from ..mappers.base import TuyaBaseConverter

_LOGGER = logging.getLogger(__name__)


class TuyaDevices(TuyaBaseConverter):
    def __init__(self):
        super().__init__("devices", self._get_devices)

    def _get_devices(self):
        """Do initialization of test dependencies instances, Returns None."""
        _LOGGER.info("Initialize")

        self._add_custom_devices()

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

                domain_fields = PLATFORM_FIELDS.get(domain, [])

                device_category_items_json = json.dumps(
                    device_category_items, cls=EnhancedJSONEncoder, indent=4
                )
                objs = json.loads(device_category_items_json)

                if not isinstance(objs, list):
                    objs = [objs]

                for obj in objs:
                    keys = list(obj)

                    for field in keys:
                        value = obj[field]
                        if (
                            field not in domain_fields or value is None
                        ) and field != "key":
                            del obj[field]

                devices[device_category_key][domain] = objs

        for domain in data_mapping:
            device_categories = data_mapping.get(domain)

            for device_category_key in device_categories:
                if device_category_key not in devices:
                    devices[device_category_key] = {}

                devices[device_category_key][domain] = True

        return devices

    @staticmethod
    def _add_custom_devices():
        _LOGGER.info("Custom devices")
