"""Test."""
from __future__ import annotations

import asyncio
import dataclasses
import json
import logging
import os
import sys

from tuya_iot import TuyaCloudOpenAPIEndpoint

from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_MILLIGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_BILLION,
    CONCENTRATION_PARTS_PER_MILLION,
    ELECTRIC_CURRENT_MILLIAMPERE,
    ELECTRIC_POTENTIAL_MILLIVOLT,
    ENERGY_KILO_WATT_HOUR,
    ENERGY_WATT_HOUR,
    LIGHT_LUX,
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
    Platform,
)
from tuya_ce.helpers.tuya_mapping import *
from tuya_ce.models.country import Country
from tuya_ce.models.unit_of_measurement import UnitOfMeasurement

DEBUG = str(os.environ.get("DEBUG", False)).lower() == str(True).lower()

log_level = logging.DEBUG if DEBUG else logging.INFO

root = logging.getLogger()
root.setLevel(log_level)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(log_level)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
stream_handler.setFormatter(formatter)
root.addHandler(stream_handler)

_LOGGER = logging.getLogger(__name__)


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)

        elif isinstance(obj, set):
            return list(obj)

        return super().default(obj)


# A tuple of available units of measurements we can work with.
# Tuya's devices aren't consistent in UOM use, thus this provides
# a list of aliases for units and possible conversions we can do
# to make them compatible with our model.
class TuyaUnits:
    _device_class_mapping: dict[str, dict[str, UnitOfMeasurement]]
    _units: list[UnitOfMeasurement]

    def __init__(self):
        self._units = self.get_units()
        self._device_class_mapping = self._get_device_class_mapping()

    def _get_device_class_mapping(self) -> dict[str, dict[str, UnitOfMeasurement]]:
        device_class_mapping: dict[str, dict[str, UnitOfMeasurement]] = {}

        for uom in self._units:
            for device_class in uom.device_classes:
                device_class_mapping.setdefault(device_class, {})[uom.unit] = uom

                if uom.aliases is not None:
                    for unit_alias in uom.aliases:
                        device_class_mapping[device_class][unit_alias] = uom

        return device_class_mapping

    @property
    def device_class_mapping(self):
        return self._device_class_mapping

    @property
    def units(self):
        return self._units

    @staticmethod
    def get_units() -> list[UnitOfMeasurement]:
        units = [
            UnitOfMeasurement(
                unit="",
                aliases=[" "],
                device_classes=[
                    SensorDeviceClass.AQI,
                    SensorDeviceClass.DATE,
                    SensorDeviceClass.MONETARY,
                    SensorDeviceClass.TIMESTAMP,
                ],
            ),
            UnitOfMeasurement(
                unit=PERCENTAGE,
                aliases=["pct", "percent", "% RH"],
                device_classes=[
                    SensorDeviceClass.BATTERY,
                    SensorDeviceClass.HUMIDITY,
                    SensorDeviceClass.POWER_FACTOR,
                ],
            ),
            UnitOfMeasurement(
                unit=CONCENTRATION_PARTS_PER_MILLION,
                device_classes=[
                    SensorDeviceClass.CO,
                    SensorDeviceClass.CO2,
                ],
            ),
            UnitOfMeasurement(
                unit=CONCENTRATION_PARTS_PER_BILLION,
                device_classes=[
                    SensorDeviceClass.CO,
                    SensorDeviceClass.CO2,
                ],
                conversion_unit=CONCENTRATION_PARTS_PER_MILLION,
            ),
            UnitOfMeasurement(
                unit=ELECTRIC_CURRENT_AMPERE,
                aliases=["a", "ampere"],
                device_classes=[SensorDeviceClass.CURRENT],
            ),
            UnitOfMeasurement(
                unit=ELECTRIC_CURRENT_MILLIAMPERE,
                aliases=["ma", "milliampere"],
                device_classes=[SensorDeviceClass.CURRENT],
                conversion_unit=ELECTRIC_CURRENT_AMPERE,
            ),
            UnitOfMeasurement(
                unit=ENERGY_WATT_HOUR,
                aliases=["wh", "watthour"],
                device_classes=[SensorDeviceClass.ENERGY],
            ),
            UnitOfMeasurement(
                unit=ENERGY_KILO_WATT_HOUR,
                aliases=["kwh", "kilowatt-hour", "kW·h"],
                device_classes=[SensorDeviceClass.ENERGY],
            ),
            UnitOfMeasurement(
                unit=VOLUME_CUBIC_FEET,
                aliases=["ft3"],
                device_classes=[SensorDeviceClass.GAS],
            ),
            UnitOfMeasurement(
                unit=VOLUME_CUBIC_METERS,
                aliases=["m3"],
                device_classes=[SensorDeviceClass.GAS],
            ),
            UnitOfMeasurement(
                unit=LIGHT_LUX,
                aliases=["lux"],
                device_classes=[SensorDeviceClass.ILLUMINANCE],
            ),
            UnitOfMeasurement(
                unit="lm",
                aliases=["lum", "lumen"],
                device_classes=[SensorDeviceClass.ILLUMINANCE],
            ),
            UnitOfMeasurement(
                unit=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                aliases=["ug/m3", "µg/m3", "ug/m³"],
                device_classes=[
                    SensorDeviceClass.NITROGEN_DIOXIDE,
                    SensorDeviceClass.NITROGEN_MONOXIDE,
                    SensorDeviceClass.NITROUS_OXIDE,
                    SensorDeviceClass.OZONE,
                    SensorDeviceClass.PM1,
                    SensorDeviceClass.PM25,
                    SensorDeviceClass.PM10,
                    SensorDeviceClass.SULPHUR_DIOXIDE,
                    SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
                ],
            ),
            UnitOfMeasurement(
                unit=CONCENTRATION_MILLIGRAMS_PER_CUBIC_METER,
                aliases=["mg/m3"],
                device_classes=[
                    SensorDeviceClass.NITROGEN_DIOXIDE,
                    SensorDeviceClass.NITROGEN_MONOXIDE,
                    SensorDeviceClass.NITROUS_OXIDE,
                    SensorDeviceClass.OZONE,
                    SensorDeviceClass.PM1,
                    SensorDeviceClass.PM25,
                    SensorDeviceClass.PM10,
                    SensorDeviceClass.SULPHUR_DIOXIDE,
                    SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
                ],
                conversion_unit=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
            ),
            UnitOfMeasurement(
                unit=POWER_WATT,
                aliases=["watt"],
                device_classes=[SensorDeviceClass.POWER],
            ),
            UnitOfMeasurement(
                unit=POWER_KILO_WATT,
                aliases=["kilowatt"],
                device_classes=[SensorDeviceClass.POWER],
            ),
            UnitOfMeasurement(
                unit=PRESSURE_BAR,
                device_classes=[SensorDeviceClass.PRESSURE],
            ),
            UnitOfMeasurement(
                unit=PRESSURE_MBAR,
                aliases=["millibar"],
                device_classes=[SensorDeviceClass.PRESSURE],
            ),
            UnitOfMeasurement(
                unit=PRESSURE_HPA,
                aliases=["hpa", "hectopascal"],
                device_classes=[SensorDeviceClass.PRESSURE],
            ),
            UnitOfMeasurement(
                unit=PRESSURE_INHG,
                aliases=["inhg"],
                device_classes=[SensorDeviceClass.PRESSURE],
            ),
            UnitOfMeasurement(
                unit=PRESSURE_PSI,
                device_classes=[SensorDeviceClass.PRESSURE],
            ),
            UnitOfMeasurement(
                unit=PRESSURE_PA,
                device_classes=[SensorDeviceClass.PRESSURE],
            ),
            UnitOfMeasurement(
                unit=SIGNAL_STRENGTH_DECIBELS,
                aliases=["db"],
                device_classes=[SensorDeviceClass.SIGNAL_STRENGTH],
            ),
            UnitOfMeasurement(
                unit=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
                aliases=["dbm"],
                device_classes=[SensorDeviceClass.SIGNAL_STRENGTH],
            ),
            UnitOfMeasurement(
                unit=TEMP_CELSIUS,
                aliases=["°c", "c", "celsius", "℃"],
                device_classes=[SensorDeviceClass.TEMPERATURE],
            ),
            UnitOfMeasurement(
                unit=TEMP_FAHRENHEIT,
                aliases=["°f", "f", "fahrenheit"],
                device_classes=[SensorDeviceClass.TEMPERATURE],
            ),
            UnitOfMeasurement(
                unit=ELECTRIC_POTENTIAL_VOLT,
                aliases=["volt"],
                device_classes=[SensorDeviceClass.VOLTAGE],
            ),
            UnitOfMeasurement(
                unit=ELECTRIC_POTENTIAL_MILLIVOLT,
                aliases=["mv", "millivolt"],
                device_classes=[SensorDeviceClass.VOLTAGE],
                conversion_unit=ELECTRIC_POTENTIAL_VOLT,
            ),
        ]

        return units


class Countries:
    # https://developer.tuya.com/en/docs/iot/oem-app-data-center-distributed?id=Kafi0ku9l07qb
    all: list[Country] = [
        Country("Afghanistan", "93", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Albania", "355", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Algeria", "213", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("American Samoa", "1-684", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Andorra", "376", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Angola", "244", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Anguilla", "1-264", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Antarctica", "672", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Antigua and Barbuda", "1-268", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Argentina", "54", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Armenia", "374", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Aruba", "297", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Australia", "61", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Austria", "43", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Azerbaijan", "994", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Bahamas", "1-242", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Bahrain", "973", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Bangladesh", "880", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Barbados", "1-246", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Belarus", "375", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Belgium", "32", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Belize", "501", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Benin", "229", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Bermuda", "1-441", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Bhutan", "975", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Bolivia", "591", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Bosnia and Herzegovina", "387", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Botswana", "267", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Brazil", "55", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country(
            "British Indian Ocean Territory", "246", TuyaCloudOpenAPIEndpoint.AMERICA
        ),
        Country("British Virgin Islands", "1-284", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Brunei", "673", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Bulgaria", "359", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Burkina Faso", "226", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Burundi", "257", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Cambodia", "855", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Cameroon", "237", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Canada", "1", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Capo Verde", "238", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Cayman Islands", "1-345", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Central African Republic", "236", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Chad", "235", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Chile", "56", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("China", "86", TuyaCloudOpenAPIEndpoint.CHINA),
        Country("Christmas Island", "61"),
        Country("Cocos Islands", "61"),
        Country("Colombia", "57", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Comoros", "269", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Cook Islands", "682", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Costa Rica", "506", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Croatia", "385", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Cuba", "53"),
        Country("Curacao", "599", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Cyprus", "357", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Czech Republic", "420", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country(
            "Democratic Republic of the Congo", "243", TuyaCloudOpenAPIEndpoint.EUROPE
        ),
        Country("Denmark", "45", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Djibouti", "253", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Dominica", "1-767", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Dominican Republic", "1-809", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("East Timor", "670", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Ecuador", "593", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Egypt", "20", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("El Salvador", "503", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Equatorial Guinea", "240", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Eritrea", "291", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Estonia", "372", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Ethiopia", "251", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Falkland Islands", "500", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Faroe Islands", "298", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Fiji", "679", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Finland", "358", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("France", "33", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("French Polynesia", "689", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Gabon", "241", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Gambia", "220", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Georgia", "995", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Germany", "49", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Ghana", "233", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Gibraltar", "350", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Greece", "30", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Greenland", "299", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Grenada", "1-473", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Guam", "1-671", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Guatemala", "502", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Guernsey", "44-1481"),
        Country("Guinea", "224"),
        Country("Guinea-Bissau", "245", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Guyana", "592", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Haiti", "509", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Honduras", "504", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Hong Kong", "852", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Hungary", "36", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Iceland", "354", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("India", "91", TuyaCloudOpenAPIEndpoint.INDIA),
        Country("Indonesia", "62", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Iran", "98"),
        Country("Iraq", "964", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Ireland", "353", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Isle of Man", "44-1624"),
        Country("Israel", "972", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Italy", "39", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Ivory Coast", "225", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Jamaica", "1-876", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Japan", "81", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Jersey", "44-1534"),
        Country("Jordan", "962", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Kazakhstan", "7", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Kenya", "254", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Kiribati", "686", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Kosovo", "383"),
        Country("Kuwait", "965", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Kyrgyzstan", "996", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Laos", "856", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Latvia", "371", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Lebanon", "961", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Lesotho", "266", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Liberia", "231", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Libya", "218", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Liechtenstein", "423", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Lithuania", "370", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Luxembourg", "352", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Macao", "853", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Macedonia", "389", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Madagascar", "261", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Malawi", "265", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Malaysia", "60", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Maldives", "960", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Mali", "223", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Malta", "356", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Marshall Islands", "692", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Mauritania", "222", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Mauritius", "230", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Mayotte", "262", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Mexico", "52", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Micronesia", "691", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Moldova", "373", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Monaco", "377", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Mongolia", "976", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Montenegro", "382", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Montserrat", "1-664", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Morocco", "212", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Mozambique", "258", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Myanmar", "95", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Namibia", "264", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Nauru", "674", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Nepal", "977", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Netherlands", "31", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Netherlands Antilles", "599"),
        Country("New Caledonia", "687", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("New Zealand", "64", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Nicaragua", "505", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Niger", "227", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Nigeria", "234", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Niue", "683", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("North Korea", "850"),
        Country("Northern Mariana Islands", "1-670", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Norway", "47", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Oman", "968", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Pakistan", "92", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Palau", "680", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Palestine", "970", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Panama", "507", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Papua New Guinea", "675", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Paraguay", "595", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Peru", "51", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Philippines", "63", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Pitcairn", "64"),
        Country("Poland", "48", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Portugal", "351", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Puerto Rico", "1-787, 1-939", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Qatar", "974", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Republic of the Congo", "242", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Reunion", "262", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Romania", "40", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Russia", "7", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Rwanda", "250", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Saint Barthelemy", "590", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Saint Helena", "290"),
        Country("Saint Kitts and Nevis", "1-869", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Saint Lucia", "1-758", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Saint Martin", "590", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Saint Pierre and Miquelon", "508", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country(
            "Saint Vincent and the Grenadines", "1-784", TuyaCloudOpenAPIEndpoint.EUROPE
        ),
        Country("Samoa", "685", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("San Marino", "378", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Sao Tome and Principe", "239", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Saudi Arabia", "966", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Senegal", "221", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Serbia", "381", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Seychelles", "248", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Sierra Leone", "232", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Singapore", "65", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Sint Maarten", "1-721", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Slovakia", "421", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Slovenia", "386", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Solomon Islands", "677", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Somalia", "252", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("South Africa", "27", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("South Korea", "82", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("South Sudan", "211"),
        Country("Spain", "34", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Sri Lanka", "94", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Sudan", "249"),
        Country("Suriname", "597", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Svalbard and Jan Mayen", "4779", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Swaziland", "268", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Sweden", "46", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Switzerland", "41", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Syria", "963"),
        Country("Taiwan", "886", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Tajikistan", "992", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Tanzania", "255", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Thailand", "66", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Togo", "228", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Tokelau", "690", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Tonga", "676", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Trinidad and Tobago", "1-868", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Tunisia", "216", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Turkey", "90", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Turkmenistan", "993", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Turks and Caicos Islands", "1-649", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Tuvalu", "688", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("U.S. Virgin Islands", "1-340", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Uganda", "256", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Ukraine", "380", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("United Arab Emirates", "971", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("United Kingdom", "44", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("United States", "1", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Uruguay", "598", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Uzbekistan", "998", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Vanuatu", "678", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Vatican", "379", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Venezuela", "58", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Vietnam", "84", TuyaCloudOpenAPIEndpoint.AMERICA),
        Country("Wallis and Futuna", "681", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Western Sahara", "212", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Yemen", "967", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Zambia", "260", TuyaCloudOpenAPIEndpoint.EUROPE),
        Country("Zimbabwe", "263", TuyaCloudOpenAPIEndpoint.EUROPE),
    ]


class Test:
    """Test Class."""

    def __init__(self):
        """Do initialization of test class instance, Returns None."""

    async def initialize(self):
        """Do initialization of test dependencies instances, Returns None."""
        _LOGGER.info("Initialize")

        data_mapping = {
            Platform.CAMERA: list(CAMERAS),
            Platform.FAN: list(TUYA_SUPPORT_TYPE),
            Platform.VACUUM: list(VACUUMS),
        }

        data_items = {
            Platform.ALARM_CONTROL_PANEL: ALARM,
            Platform.BINARY_SENSOR: BINARY_SENSORS,
            Platform.BUTTON: BUTTONS,
            Platform.CLIMATE: CLIMATE_DESCRIPTIONS,
            Platform.COVER: COVERS,
            Platform.HUMIDIFIER: HUMIDIFIERS,
            Platform.LIGHT: LIGHTS,
            Platform.NUMBER: NUMBERS,
            Platform.SELECT: SELECTS,
            Platform.SENSOR: SENSORS,
            Platform.SIREN: SIRENS,
            Platform.SWITCH: SWITCHES,
        }

        devices = {}

        for domain in data_items:
            device_categories = data_items.get(domain)

            for device_category_key in device_categories:
                device_category_items = device_categories.get(device_category_key)

                if device_category_key not in devices:
                    devices[device_category_key] = {}

                devices[device_category_key][domain] = device_category_items

        for domain in data_mapping:
            device_categories = data_mapping.get(domain)

            for device_category_key in device_categories:
                if device_category_key not in devices:
                    devices[device_category_key] = {}

                devices[device_category_key][domain] = True

        countries = Countries.all
        device_class_mapping = TuyaUnits().device_class_mapping

        payload = {
            "devices": devices,
            "countries": countries,
            "device_class": device_class_mapping,
        }

        data = json.dumps(payload, cls=EnhancedJSONEncoder, indent=4)

        print(data)

    async def terminate(self):
        """Do termination of API, Returns None."""
        _LOGGER.info("Terminate")


instance = Test()
loop = asyncio.new_event_loop()

try:
    loop.run_until_complete(instance.initialize())

except KeyboardInterrupt:
    _LOGGER.info("Aborted")
    loop.run_until_complete(instance.terminate())

except Exception as rex:
    _LOGGER.error(f"Error: {rex}")
