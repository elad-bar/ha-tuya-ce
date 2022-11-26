from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_MILLIGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_BILLION,
    CONCENTRATION_PARTS_PER_MILLION,
    ELECTRIC_CURRENT_AMPERE,
    ELECTRIC_CURRENT_MILLIAMPERE,
    ELECTRIC_POTENTIAL_MILLIVOLT,
    ELECTRIC_POTENTIAL_VOLT,
    ENERGY_KILO_WATT_HOUR,
    ENERGY_WATT_HOUR,
    LIGHT_LUX,
    PERCENTAGE,
    POWER_KILO_WATT,
    POWER_WATT,
    PRESSURE_BAR,
    PRESSURE_HPA,
    PRESSURE_INHG,
    PRESSURE_MBAR,
    PRESSURE_PA,
    PRESSURE_PSI,
    SIGNAL_STRENGTH_DECIBELS,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    VOLUME_CUBIC_FEET,
    VOLUME_CUBIC_METERS,
)


@dataclass
class UnitOfMeasurement:
    """Describes a unit of measurement."""

    unit: str
    device_classes: set[str]

    aliases: set[str] = field(default_factory=set)
    conversion_unit: str | None = None
    conversion_fn: Callable[[float], float] | None = None


# A tuple of available units of measurements we can work with.
# Tuya's devices aren't consistent in UOM use, thus this provides
# a list of aliases for units and possible conversions we can do
# to make them compatible with our model.
class TuyaUnits:
    _device_class_mapping: dict[str, dict[str, UnitOfMeasurement]]
    _units: list[UnitOfMeasurement]

    def __init__(self):
        self._units = self._get_units()
        self._device_class_mapping = self._get_device_class_mapping()

    def _get_device_class_mapping(self) -> dict[str, dict[str, UnitOfMeasurement]]:
        device_class_mapping: dict[str, dict[str, UnitOfMeasurement]] = {}

        for uom in self._units:
            for device_class in uom.device_classes:
                device_class_mapping.setdefault(device_class, {})[uom.unit] = uom
                for unit_alias in uom.aliases:
                    device_class_mapping[device_class][unit_alias] = uom

        return device_class_mapping

    @property
    def device_class_mapping(self):
        return self._device_class_mapping

    @staticmethod
    def _get_units() -> list[UnitOfMeasurement]:
        units = [
            UnitOfMeasurement(
                unit="",
                aliases={" "},
                device_classes={
                    SensorDeviceClass.AQI,
                    SensorDeviceClass.DATE,
                    SensorDeviceClass.MONETARY,
                    SensorDeviceClass.TIMESTAMP,
                },
            ),
            UnitOfMeasurement(
                unit=PERCENTAGE,
                aliases={"pct", "percent", "% RH"},
                device_classes={
                    SensorDeviceClass.BATTERY,
                    SensorDeviceClass.HUMIDITY,
                    SensorDeviceClass.POWER_FACTOR,
                },
            ),
            UnitOfMeasurement(
                unit=CONCENTRATION_PARTS_PER_MILLION,
                device_classes={
                    SensorDeviceClass.CO,
                    SensorDeviceClass.CO2,
                },
            ),
            UnitOfMeasurement(
                unit=CONCENTRATION_PARTS_PER_BILLION,
                device_classes={
                    SensorDeviceClass.CO,
                    SensorDeviceClass.CO2,
                },
                conversion_unit=CONCENTRATION_PARTS_PER_MILLION,
                conversion_fn=lambda x: x / 1000,
            ),
            UnitOfMeasurement(
                unit=ELECTRIC_CURRENT_AMPERE,
                aliases={"a", "ampere"},
                device_classes={SensorDeviceClass.CURRENT},
            ),
            UnitOfMeasurement(
                unit=ELECTRIC_CURRENT_MILLIAMPERE,
                aliases={"ma", "milliampere"},
                device_classes={SensorDeviceClass.CURRENT},
                conversion_unit=ELECTRIC_CURRENT_AMPERE,
                conversion_fn=lambda x: x / 1000,
            ),
            UnitOfMeasurement(
                unit=ENERGY_WATT_HOUR,
                aliases={"wh", "watthour"},
                device_classes={SensorDeviceClass.ENERGY},
            ),
            UnitOfMeasurement(
                unit=ENERGY_KILO_WATT_HOUR,
                aliases={"kwh", "kilowatt-hour", "kW·h"},
                device_classes={SensorDeviceClass.ENERGY},
            ),
            UnitOfMeasurement(
                unit=VOLUME_CUBIC_FEET,
                aliases={"ft3"},
                device_classes={SensorDeviceClass.GAS},
            ),
            UnitOfMeasurement(
                unit=VOLUME_CUBIC_METERS,
                aliases={"m3"},
                device_classes={SensorDeviceClass.GAS},
            ),
            UnitOfMeasurement(
                unit=LIGHT_LUX,
                aliases={"lux"},
                device_classes={SensorDeviceClass.ILLUMINANCE},
            ),
            UnitOfMeasurement(
                unit="lm",
                aliases={"lum", "lumen"},
                device_classes={SensorDeviceClass.ILLUMINANCE},
            ),
            UnitOfMeasurement(
                unit=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                aliases={"ug/m3", "µg/m3", "ug/m³"},
                device_classes={
                    SensorDeviceClass.NITROGEN_DIOXIDE,
                    SensorDeviceClass.NITROGEN_MONOXIDE,
                    SensorDeviceClass.NITROUS_OXIDE,
                    SensorDeviceClass.OZONE,
                    SensorDeviceClass.PM1,
                    SensorDeviceClass.PM25,
                    SensorDeviceClass.PM10,
                    SensorDeviceClass.SULPHUR_DIOXIDE,
                    SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
                },
            ),
            UnitOfMeasurement(
                unit=CONCENTRATION_MILLIGRAMS_PER_CUBIC_METER,
                aliases={"mg/m3"},
                device_classes={
                    SensorDeviceClass.NITROGEN_DIOXIDE,
                    SensorDeviceClass.NITROGEN_MONOXIDE,
                    SensorDeviceClass.NITROUS_OXIDE,
                    SensorDeviceClass.OZONE,
                    SensorDeviceClass.PM1,
                    SensorDeviceClass.PM25,
                    SensorDeviceClass.PM10,
                    SensorDeviceClass.SULPHUR_DIOXIDE,
                    SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
                },
                conversion_unit=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                conversion_fn=lambda x: x * 1000,
            ),
            UnitOfMeasurement(
                unit=POWER_WATT,
                aliases={"watt"},
                device_classes={SensorDeviceClass.POWER},
            ),
            UnitOfMeasurement(
                unit=POWER_KILO_WATT,
                aliases={"kilowatt"},
                device_classes={SensorDeviceClass.POWER},
            ),
            UnitOfMeasurement(
                unit=PRESSURE_BAR,
                device_classes={SensorDeviceClass.PRESSURE},
            ),
            UnitOfMeasurement(
                unit=PRESSURE_MBAR,
                aliases={"millibar"},
                device_classes={SensorDeviceClass.PRESSURE},
            ),
            UnitOfMeasurement(
                unit=PRESSURE_HPA,
                aliases={"hpa", "hectopascal"},
                device_classes={SensorDeviceClass.PRESSURE},
            ),
            UnitOfMeasurement(
                unit=PRESSURE_INHG,
                aliases={"inhg"},
                device_classes={SensorDeviceClass.PRESSURE},
            ),
            UnitOfMeasurement(
                unit=PRESSURE_PSI,
                device_classes={SensorDeviceClass.PRESSURE},
            ),
            UnitOfMeasurement(
                unit=PRESSURE_PA,
                device_classes={SensorDeviceClass.PRESSURE},
            ),
            UnitOfMeasurement(
                unit=SIGNAL_STRENGTH_DECIBELS,
                aliases={"db"},
                device_classes={SensorDeviceClass.SIGNAL_STRENGTH},
            ),
            UnitOfMeasurement(
                unit=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
                aliases={"dbm"},
                device_classes={SensorDeviceClass.SIGNAL_STRENGTH},
            ),
            UnitOfMeasurement(
                unit=TEMP_CELSIUS,
                aliases={"°c", "c", "celsius", "℃"},
                device_classes={SensorDeviceClass.TEMPERATURE},
            ),
            UnitOfMeasurement(
                unit=TEMP_FAHRENHEIT,
                aliases={"°f", "f", "fahrenheit"},
                device_classes={SensorDeviceClass.TEMPERATURE},
            ),
            UnitOfMeasurement(
                unit=ELECTRIC_POTENTIAL_VOLT,
                aliases={"volt"},
                device_classes={SensorDeviceClass.VOLTAGE},
            ),
            UnitOfMeasurement(
                unit=ELECTRIC_POTENTIAL_MILLIVOLT,
                aliases={"mv", "millivolt"},
                device_classes={SensorDeviceClass.VOLTAGE},
                conversion_unit=ELECTRIC_POTENTIAL_VOLT,
                conversion_fn=lambda x: x / 1000,
            )
        ]

        return units
