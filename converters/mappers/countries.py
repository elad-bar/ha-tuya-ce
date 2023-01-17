from converters.mappers.base import TuyaBaseConverter
from homeassistant.components.tuya.const import TUYA_COUNTRIES


class TuyaCountries(TuyaBaseConverter):
    def __init__(self):
        super().__init__("countries", self._get_countries)

    @staticmethod
    def _get_countries() -> list:
        return TUYA_COUNTRIES
