from __future__ import annotations

from collections.abc import Callable

from tuya_iot import TuyaDeviceManager

from homeassistant.helpers.entity import EntityDescription


class TuyaPlatform:
    name: str
    get_entity_description: Callable[[dict], EntityDescription] | None
    validate: Callable[[dict | bool, TuyaDeviceManager], bool]
    fields: list[str] | None

    def __init__(self,
                 name: str,
                 fields: list[str] | None = None,
                 get_entity_description: Callable[[dict], EntityDescription] | None = None,
                 validate: Callable[[dict | bool, TuyaDeviceManager], bool] = lambda e, d: e.get("key") in d.status):

        self.name = name
        self.get_entity_description = get_entity_description
        self.validate = validate
        self.fields = fields
