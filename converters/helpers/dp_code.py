from homeassistant.backports.enum import StrEnum
from homeassistant.components.tuya import DPCode


class ExtendedDPCode(StrEnum):
    """Data Point Codes used by Tuya.

    https://developer.tuya.com/en/docs/iot/standarddescription?id=K9i5ql6waswzq
    """
    AREA_1 = "areaone"
    AREA_2 = "areatwo"
    AREA_3 = "areathree"
    AREA_4 = "areafour"
    AREA_5 = "areafive"
    AREA_6 = "areasix"
    AREA_7 = "areaseven"
    AREA_8 = "areaeight"
    BODY_RESISTANCE = "BR"
    LEFT_HAND_RESISTANCE = "LResistance"
    LEFT_LEG_RESISTANCE = "LLR"
    RIGHT_HAND_RESISTANCE = "RHR"
    RIGHT_LEG_RESISTANCE = "RLR"
    SMART_WEATHER = "smart_weather"
    QUICK_START = "quickstart"
    WEIGHT = "weight"
    WEIGHT_COUNT = "weightcount"
    WEATHER = "weather"
