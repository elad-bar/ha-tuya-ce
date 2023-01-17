"""Support for Tuya cameras."""
from __future__ import annotations

from abc import ABC

from tuya_iot import TuyaDevice, TuyaDeviceManager

from homeassistant.components import ffmpeg
from homeassistant.components.camera import Camera as CameraEntity, CameraEntityFeature
from homeassistant.components.tuya import DPCode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .managers.tuya_configuration_manager import TuyaConfigurationManager
from .models.base import TuyaEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Tuya cameras dynamically through Tuya discovery."""
    manager = TuyaConfigurationManager.get_instance(hass)
    await manager.async_setup_entry(Platform.CAMERA,
                                    entry,
                                    async_add_entities,
                                    TuyaCameraEntity.create_entity)


class TuyaCameraEntity(TuyaEntity, CameraEntity, ABC):
    """Tuya Camera Entity."""

    _attr_supported_features = CameraEntityFeature.STREAM
    _attr_brand = "Tuya"

    def __init__(
        self,
        hass: HomeAssistant,
        device: TuyaDevice,
        device_manager: TuyaDeviceManager,
    ) -> None:
        """Init Tuya Camera."""
        super().__init__(hass, device, device_manager)
        CameraEntity.__init__(self)
        self._attr_model = device.product_name

    @staticmethod
    def create_entity(hass: HomeAssistant,
                      device: TuyaDevice,
                      device_manager: TuyaDeviceManager):
        instance = TuyaCameraEntity(hass, device, device_manager)

        return instance

    @property
    def is_recording(self) -> bool:
        """Return true if the device is recording."""
        return self.device.status.get(DPCode.RECORD_SWITCH, False)

    @property
    def motion_detection_enabled(self) -> bool:
        """Return the camera motion detection status."""
        return self.device.status.get(DPCode.MOTION_SWITCH, False)

    async def stream_source(self) -> str | None:
        """Return the source of the stream."""
        return await self.hass.async_add_executor_job(
            self.device_manager.get_device_stream_allocate,
            self.device.id,
            "rtsp",
        )

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return a still image response from the camera."""
        stream_source = await self.stream_source()
        if not stream_source:
            return None
        return await ffmpeg.async_get_image(
            self.hass,
            stream_source,
            width=width,
            height=height,
        )

    def enable_motion_detection(self) -> None:
        """Enable motion detection in the camera."""
        self._send_command([{"code": DPCode.MOTION_SWITCH, "value": True}])

    def disable_motion_detection(self) -> None:
        """Disable motion detection in camera."""
        self._send_command([{"code": DPCode.MOTION_SWITCH, "value": False}])
