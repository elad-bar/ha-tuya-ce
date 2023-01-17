from __future__ import annotations

from collections.abc import Callable
import json

from converters.helpers.enhanced_json_encoder import EnhancedJSONEncoder


class TuyaBaseConverter:
    _data: list | dict
    _name: str

    def __init__(self, name: str, data_provider: Callable[[], [list | dict]]):
        self._data = data_provider()
        self._name = name

    @property
    def all(self) -> list | dict:
        return self._data

    def save(self):
        data = json.dumps(self._data, cls=EnhancedJSONEncoder, indent=4)

        with open(f"../config/{self._name}.json", "w") as outfile:
            outfile.write(data)
