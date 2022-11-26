from typing import NamedTuple

from tuya_iot import TuyaDeviceListener, TuyaDeviceManager, TuyaHomeManager


class HomeAssistantTuyaData(NamedTuple):
    """Tuya data stored in the Home Assistant data object."""

    device_listener: TuyaDeviceListener
    device_manager: TuyaDeviceManager
    home_manager: TuyaHomeManager
