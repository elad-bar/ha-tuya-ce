from dataclasses import dataclass

from ..helpers.enums.dp_code import DPCode
from .base import IntegerTypeData


@dataclass
class ColorTypeData:
    """Color Type Data."""

    h_type: IntegerTypeData
    s_type: IntegerTypeData
    v_type: IntegerTypeData


@dataclass
class ColorTypes:
    v1: ColorTypeData = ColorTypeData(
            h_type=IntegerTypeData(DPCode.COLOUR_DATA_HSV, min=1, scale=0, max=360, step=1),
            s_type=IntegerTypeData(DPCode.COLOUR_DATA_HSV, min=1, scale=0, max=255, step=1),
            v_type=IntegerTypeData(DPCode.COLOUR_DATA_HSV, min=1, scale=0, max=255, step=1),
        )

    v2: ColorTypeData = ColorTypeData(
            h_type=IntegerTypeData(DPCode.COLOUR_DATA_HSV, min=1, scale=0, max=360, step=1),
            s_type=IntegerTypeData(DPCode.COLOUR_DATA_HSV, min=1, scale=0, max=1000, step=1),
            v_type=IntegerTypeData(DPCode.COLOUR_DATA_HSV, min=1, scale=0, max=1000, step=1),
        )
