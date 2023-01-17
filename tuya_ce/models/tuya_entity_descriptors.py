from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.climate import ClimateEntityDescription, HVACMode
from homeassistant.components.cover import CoverEntityDescription
from homeassistant.components.humidifier import HumidifierEntityDescription
from homeassistant.components.light import LightEntityDescription
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.components.tuya import DPCode

from .color_type_data import ColorTypeData, ColorTypes


@dataclass
class T1uyaBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a Tuya binary sensor."""

    # DPCode, to use. If None, the key will be used as DPCode
    dpcode: DPCode | None = None

    # Value or values to consider binary sensor to be "on"
    on_value: bool | float | int | str | set[bool | float | int | str] = True


@dataclass
class T1uyaClimateEntityDescription(ClimateEntityDescription):
    """Describe an Tuya climate entity."""
    switch_only_hvac_mode: HVACMode = HVACMode.OFF


@dataclass
class T1uyaCoverEntityDescription(CoverEntityDescription):
    """Describe an Tuya cover entity."""

    current_state: DPCode | None = None
    current_state_inverse: bool = False
    current_position: DPCode | tuple[DPCode, ...] | None = None
    set_position: DPCode | None = None
    open_instruction_value: str = "open"
    close_instruction_value: str = "close"
    stop_instruction_value: str = "stop"


@dataclass
class T1uyaHumidifierEntityDescription(HumidifierEntityDescription):
    """Describe an Tuya (de)humidifier entity."""

    # DPCode, to use. If None, the key will be used as DPCode
    dpcode: DPCode | tuple[DPCode, ...] | None = None

    humidity: DPCode | None = None


@dataclass
class T1uyaLightEntityDescription(LightEntityDescription):
    """Describe an Tuya light entity."""

    brightness_max: DPCode | None = None
    brightness_min: DPCode | None = None
    brightness: DPCode | tuple[DPCode, ...] | None = None
    color_data: DPCode | tuple[DPCode, ...] | None = None
    color_mode: DPCode | None = None
    color_temp: DPCode | tuple[DPCode, ...] | None = None
    default_color_type: ColorTypeData = ColorTypes.v1


@dataclass
class T1uyaSensorEntityDescription1(SensorEntityDescription):
    """Describes Tuya sensor entity."""

    subkey: str | None = None
