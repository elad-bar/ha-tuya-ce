"""Test."""
from __future__ import annotations

import asyncio
import json
import logging
import os
import sys

from converters.mappers.countries import TuyaCountries
from converters.mappers.devices import TuyaDevices
from converters.mappers.ha import HAMapper
from converters.mappers.units import TuyaUnits

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


class App:
    """Test Class."""

    def __init__(self):
        """Do initialization of test class instance, Returns None."""

    async def gap_analysis(self, file_name):
        with open(f"../input/{file_name}") as file:
            json_data = json.load(file)

        data = json_data.get("data")

        _LOGGER.debug("before mapper")

        mapper = HAMapper()

        _LOGGER.debug("mapper")

        result = await mapper.gap_analysis(data)

        _LOGGER.info(json.dumps(result))

    async def update_configuration_files(self):
        """Update configuration files, Returns None."""
        _LOGGER.info("Update configuration files")

        mappers = [
            TuyaCountries(),
            TuyaUnits(),
            TuyaDevices()
        ]

        for mapper in mappers:
            mapper.save()

    async def terminate(self):
        """Do termination of API, Returns None."""
        _LOGGER.info("Terminate")


instance = App()
loop = asyncio.new_event_loop()

try:
    # loop.run_until_complete(instance.update_configuration_files())

    loop.run_until_complete(instance.gap_analysis("t22.json"))


except KeyboardInterrupt:
    _LOGGER.info("Aborted")
    loop.run_until_complete(instance.terminate())

except Exception as rex:
    _LOGGER.error(f"Error: {rex}")
