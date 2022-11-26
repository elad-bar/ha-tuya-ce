"""Support for the Tuya lights."""
from __future__ import annotations

import json
from typing import Any, cast

from tuya_iot import TuyaDevice, TuyaDeviceManager

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_HS_COLOR,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .helpers.enums.dp_code import DPCode
from .helpers.enums.dp_type import DPType
from .helpers.enums.work_mode import WorkMode
from .helpers.util import remap_value
from .managers.tuya_device_configuration_manager import TuyaDeviceConfigurationManager
from .models.base import IntegerTypeData, TuyaEntity
from .models.color_data import ColorData
from .models.color_type_data import ColorTypeData, ColorTypes
from .models.tuya_entity_descriptors import TuyaLightEntityDescription


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up tuya light dynamically through tuya discovery."""
    manager = TuyaDeviceConfigurationManager.get_instance(hass)
    await manager.async_setup_entry(Platform.LIGHT,
                                    entry,
                                    async_add_entities,
                                    TuyaLightEntity.create_entity)


class TuyaLightEntity(TuyaEntity, LightEntity):
    """Tuya light device."""

    entity_description: TuyaLightEntityDescription

    _brightness_max: IntegerTypeData | None = None
    _brightness_min: IntegerTypeData | None = None
    _brightness: IntegerTypeData | None = None
    _color_data_dpcode: DPCode | None = None
    _color_data_type: ColorTypeData | None = None
    _color_mode: DPCode | None = None
    _color_temp: IntegerTypeData | None = None

    def __init__(
        self,
        device: TuyaDevice,
        device_manager: TuyaDeviceManager,
        description: TuyaLightEntityDescription,
    ) -> None:
        """Init TuyaHaLight."""
        super().__init__(device, device_manager)
        self.entity_description = description
        self._attr_unique_id = f"{super().unique_id}{description.key}"
        self._attr_supported_color_modes: set[ColorMode] = set()

        # Determine DPCodes
        self._color_mode_dpcode = self.find_dpcode(
            description.color_mode, prefer_function=True
        )

        if int_type := self.find_dpcode(
            description.brightness, dptype=DPType.INTEGER, prefer_function=True
        ):
            self._brightness = int_type
            self._attr_supported_color_modes.add(ColorMode.BRIGHTNESS)
            self._brightness_max = self.find_dpcode(
                description.brightness_max, dptype=DPType.INTEGER
            )
            self._brightness_min = self.find_dpcode(
                description.brightness_min, dptype=DPType.INTEGER
            )

        if int_type := self.find_dpcode(
            description.color_temp, dptype=DPType.INTEGER, prefer_function=True
        ):
            self._color_temp = int_type
            self._attr_supported_color_modes.add(ColorMode.COLOR_TEMP)

        if (
            dpcode := self.find_dpcode(description.color_data, prefer_function=True)
        ) and self.get_dptype(dpcode) == DPType.JSON:
            self._color_data_dpcode = dpcode
            self._attr_supported_color_modes.add(ColorMode.HS)
            if dpcode in self.device.function:
                values = cast(str, self.device.function[dpcode].values)
            else:
                values = self.device.status_range[dpcode].values

            # Fetch color data type information
            if function_data := json.loads(values):
                self._color_data_type = ColorTypeData(
                    h_type=IntegerTypeData(dpcode, **function_data["h"]),
                    s_type=IntegerTypeData(dpcode, **function_data["s"]),
                    v_type=IntegerTypeData(dpcode, **function_data["v"]),
                )
            else:
                # If no type is found, use a default one
                self._color_data_type = self.entity_description.default_color_type
                if self._color_data_dpcode == DPCode.COLOUR_DATA_V2 or (
                    self._brightness and self._brightness.max > 255
                ):
                    self._color_data_type = ColorTypes.v2

        if not self._attr_supported_color_modes:
            self._attr_supported_color_modes = {ColorMode.ONOFF}

    @staticmethod
    def create_entity(device: TuyaDevice,
                      device_manager: TuyaDeviceManager,
                      description: TuyaLightEntityDescription):
        instance = TuyaLightEntity(device, device_manager, description)

        return instance

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self.device.status.get(self.entity_description.key, False)

    def turn_on(self, **kwargs: Any) -> None:
        """Turn on or control the light."""
        commands = [{"code": self.entity_description.key, "value": True}]

        if self._color_temp and ATTR_COLOR_TEMP in kwargs:
            if self._color_mode_dpcode:
                commands += [
                    {
                        "code": self._color_mode_dpcode,
                        "value": WorkMode.WHITE,
                    },
                ]

            commands += [
                {
                    "code": self._color_temp.dpcode,
                    "value": round(
                        self._color_temp.remap_value_from(
                            kwargs[ATTR_COLOR_TEMP],
                            self.min_mireds,
                            self.max_mireds,
                            reverse=True,
                        )
                    ),
                },
            ]
        elif self._color_data_type and (
            ATTR_HS_COLOR in kwargs
            or (ATTR_BRIGHTNESS in kwargs and self.color_mode == ColorMode.HS)
        ):
            if self._color_mode_dpcode:
                commands += [
                    {
                        "code": self._color_mode_dpcode,
                        "value": WorkMode.COLOUR,
                    },
                ]

            if not (brightness := kwargs.get(ATTR_BRIGHTNESS)):
                brightness = self.brightness or 0

            if not (color := kwargs.get(ATTR_HS_COLOR)):
                color = self.hs_color or (0, 0)

            commands += [
                {
                    "code": self._color_data_dpcode,
                    "value": json.dumps(
                        {
                            "h": round(
                                self._color_data_type.h_type.remap_value_from(
                                    color[0], 0, 360
                                )
                            ),
                            "s": round(
                                self._color_data_type.s_type.remap_value_from(
                                    color[1], 0, 100
                                )
                            ),
                            "v": round(
                                self._color_data_type.v_type.remap_value_from(
                                    brightness
                                )
                            ),
                        }
                    ),
                },
            ]

        if (
            ATTR_BRIGHTNESS in kwargs
            and self.color_mode != ColorMode.HS
            and self._brightness
        ):
            brightness = kwargs[ATTR_BRIGHTNESS]

            # If there is a min/max value, the brightness is actually limited.
            # Meaning it is actually not on a 0-255 scale.
            if (
                self._brightness_max is not None
                and self._brightness_min is not None
                and (
                    brightness_max := self.device.status.get(
                        self._brightness_max.dpcode
                    )
                )
                is not None
                and (
                    brightness_min := self.device.status.get(
                        self._brightness_min.dpcode
                    )
                )
                is not None
            ):
                # Remap values onto our scale
                brightness_max = self._brightness_max.remap_value_to(brightness_max)
                brightness_min = self._brightness_min.remap_value_to(brightness_min)

                # Remap the brightness value from their min-max to our 0-255 scale
                brightness = remap_value(
                    brightness,
                    to_min=brightness_min,
                    to_max=brightness_max,
                )

            commands += [
                {
                    "code": self._brightness.dpcode,
                    "value": round(self._brightness.remap_value_from(brightness)),
                },
            ]

        self._send_command(commands)

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._send_command([{"code": self.entity_description.key, "value": False}])

    @property
    def brightness(self) -> int | None:
        """Return the brightness of the light."""
        # If the light is currently in color mode, extract the brightness from the color data
        if self.color_mode == ColorMode.HS and (color_data := self._get_color_data()):
            return color_data.brightness

        if not self._brightness:
            return None

        brightness = self.device.status.get(self._brightness.dpcode)
        if brightness is None:
            return None

        # Remap value to our scale
        brightness = self._brightness.remap_value_to(brightness)

        # If there is a min/max value, the brightness is actually limited.
        # Meaning it is actually not on a 0-255 scale.
        if (
            self._brightness_max is not None
            and self._brightness_min is not None
            and (brightness_max := self.device.status.get(self._brightness_max.dpcode))
            is not None
            and (brightness_min := self.device.status.get(self._brightness_min.dpcode))
            is not None
        ):
            # Remap values onto our scale
            brightness_max = self._brightness_max.remap_value_to(brightness_max)
            brightness_min = self._brightness_min.remap_value_to(brightness_min)

            # Remap the brightness value from their min-max to our 0-255 scale
            brightness = remap_value(
                brightness,
                from_min=brightness_min,
                from_max=brightness_max,
            )

        return round(brightness)

    @property
    def color_temp(self) -> int | None:
        """Return the color_temp of the light."""
        if not self._color_temp:
            return None

        temperature = self.device.status.get(self._color_temp.dpcode)
        if temperature is None:
            return None

        return round(
            self._color_temp.remap_value_to(
                temperature, self.min_mireds, self.max_mireds, reverse=True
            )
        )

    @property
    def hs_color(self) -> tuple[float, float] | None:
        """Return the hs_color of the light."""
        if self._color_data_dpcode is None or not (
            color_data := self._get_color_data()
        ):
            return None
        return color_data.hs_color

    @property
    def color_mode(self) -> ColorMode:
        """Return the color_mode of the light."""
        # We consider it to be in HS color mode, when work mode is anything
        # else than "white".
        if (
            self._color_mode_dpcode
            and self.device.status.get(self._color_mode_dpcode) != WorkMode.WHITE
        ):
            return ColorMode.HS
        if self._color_temp:
            return ColorMode.COLOR_TEMP
        if self._brightness:
            return ColorMode.BRIGHTNESS
        return ColorMode.ONOFF

    def _get_color_data(self) -> ColorData | None:
        """Get current color data from device."""
        if (
            self._color_data_type is None
            or self._color_data_dpcode is None
            or self._color_data_dpcode not in self.device.status
        ):
            return None

        if not (status_data := self.device.status[self._color_data_dpcode]):
            return None

        if not (status := json.loads(status_data)):
            return None

        return ColorData(
            type_data=self._color_data_type,
            h_value=status["h"],
            s_value=status["s"],
            v_value=status["v"],
        )
