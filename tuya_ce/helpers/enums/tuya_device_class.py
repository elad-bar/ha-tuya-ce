from homeassistant.backports.enum import StrEnum


class TuyaDeviceClass(StrEnum):
    """Tuya specific device classes, used for translations."""

    AIR_QUALITY = "tuya__air_quality"
    CURTAIN_MODE = "tuya__curtain_mode"
    CURTAIN_MOTOR_MODE = "tuya__curtain_motor_mode"
    BASIC_ANTI_FLICKR = "tuya__basic_anti_flickr"
    BASIC_NIGHTVISION = "tuya__basic_nightvision"
    COUNTDOWN = "tuya__countdown"
    DECIBEL_SENSITIVITY = "tuya__decibel_sensitivity"
    FAN_ANGLE = "tuya__fan_angle"
    FINGERBOT_MODE = "tuya__fingerbot_mode"
    HUMIDIFIER_SPRAY_MODE = "tuya__humidifier_spray_mode"
    HUMIDIFIER_LEVEL = "tuya__humidifier_level"
    HUMIDIFIER_MOODLIGHTING = "tuya__humidifier_moodlighting"
    IPC_WORK_MODE = "tuya__ipc_work_mode"
    LED_TYPE = "tuya__led_type"
    LIGHT_MODE = "tuya__light_mode"
    MOTION_SENSITIVITY = "tuya__motion_sensitivity"
    RECORD_MODE = "tuya__record_mode"
    RELAY_STATUS = "tuya__relay_status"
    STATUS = "tuya__status"
    VACUUM_CISTERN = "tuya__vacuum_cistern"
    VACUUM_COLLECTION = "tuya__vacuum_collection"
    VACUUM_MODE = "tuya__vacuum_mode"
