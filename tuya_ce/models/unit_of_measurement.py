from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.tuya.const import UnitOfMeasurement
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_MILLIGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_BILLION,
    CONCENTRATION_PARTS_PER_MILLION,
    ELECTRIC_CURRENT_AMPERE,
    ELECTRIC_CURRENT_MILLIAMPERE,
    ELECTRIC_POTENTIAL_MILLIVOLT,
    ELECTRIC_POTENTIAL_VOLT,
    UnitOfMass,
)


@dataclass
class ExtendedUnitOfMeasurement:
    """Describes a unit of measurement."""

    unit: str
    device_classes: list[str]

    aliases: list[str] | None = None
    conversion_unit: str | None = None

    def __init__(self,
                 unit: str,
                 device_classes: list[str],
                 aliases: list[str] | None = None,
                 conversion_unit: str | None = None):

        self.unit = unit
        self.device_classes = device_classes
        self.aliases = aliases
        self.conversion_unit = conversion_unit

        self._conversion_fn_mapping = {
            f"{CONCENTRATION_PARTS_PER_BILLION}_{CONCENTRATION_PARTS_PER_MILLION}":
                lambda x: x / 1000,

            f"{ELECTRIC_CURRENT_MILLIAMPERE}_{ELECTRIC_CURRENT_AMPERE}":
                lambda x: x / 1000,

            f"{CONCENTRATION_MILLIGRAMS_PER_CUBIC_METER}_{CONCENTRATION_MICROGRAMS_PER_CUBIC_METER}":
                lambda x: x * 1000,

            f"{ELECTRIC_POTENTIAL_MILLIVOLT}_{ELECTRIC_POTENTIAL_VOLT}":
                lambda x: x / 1000,

            f"{UnitOfMass.GRAMS}_{UnitOfMass.KILOGRAMS}":
                lambda x: x / 1000,
        }

    @staticmethod
    def from_dict(data: dict):
        unit: str = data.get("unit")
        device_classes: list[str] = data.get("unit")
        aliases: list[str] | None = data.get("aliases")
        conversion_unit: str | None = data.get("conversion_unit")

        instance = ExtendedUnitOfMeasurement(unit, device_classes, aliases, conversion_unit)

        return instance

    @staticmethod
    def from_ha_unit(data: UnitOfMeasurement):
        unit: str = data.unit
        device_classes: list[str] = list(data.device_classes)
        aliases: list[str] | None = list(data.aliases)
        conversion_unit: str | None = data.conversion_unit

        instance = ExtendedUnitOfMeasurement(unit, device_classes, aliases, conversion_unit)

        return instance

    def conversion_fn(self, value):
        key = f"{self.unit}_{self.conversion_unit}"
        conversion_func = self._conversion_fn_mapping.get(key)

        if conversion_func is not None:
            value = conversion_func(value)

        return value
