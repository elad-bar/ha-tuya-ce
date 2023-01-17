"""Unit's mapper."""
from __future__ import annotations

import logging

from converters.mappers.base import TuyaBaseConverter
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.tuya.const import UNITS
from homeassistant.const import UnitOfMass
from tuya_ce.models.unit_of_measurement import (
    ExtendedUnitOfMeasurement,
    UnitOfMeasurement,
)

_LOGGER = logging.getLogger(__name__)


# A tuple of available units of measurements we can work with.
# Tuya's devices aren't consistent in UOM use, thus this provides
# a list of aliases for units and possible conversions we can do
# to make them compatible with our model.
class TuyaUnits(TuyaBaseConverter):
    _units: list[ExtendedUnitOfMeasurement]

    def __init__(self):
        super().__init__("units", self._get_device_class_mapping)

    def _get_device_class_mapping(self) -> dict[str, dict[str, ExtendedUnitOfMeasurement]]:
        units = self._get_units()
        device_class_mapping: dict[str, dict[str, ExtendedUnitOfMeasurement]] = {}

        for uom in units:
            for device_class in uom.device_classes:
                device_class_mapping.setdefault(device_class, {})[uom.unit] = uom

                if uom.aliases is not None:
                    for unit_alias in uom.aliases:
                        device_class_mapping[device_class][unit_alias] = uom

        return device_class_mapping

    @staticmethod
    def _get_units() -> list[ExtendedUnitOfMeasurement]:
        tuya_units = list(UNITS)

        gram = UnitOfMeasurement(
            unit=UnitOfMass.GRAMS,
            aliases={"g"},
            device_classes={SensorDeviceClass.WEIGHT},
            conversion_unit=UnitOfMass.KILOGRAMS
        )

        tuya_units.append(gram)

        units: list[ExtendedUnitOfMeasurement] = []

        for unit in tuya_units:
            extended_unit = ExtendedUnitOfMeasurement.from_ha_unit(unit)

            units.append(extended_unit)

        return units
