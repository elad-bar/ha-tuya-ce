"""Constants for the Tuya integration."""
from __future__ import annotations

from homeassistant.components.climate import HVACMode
from homeassistant.components.tuya.alarm_control_panel import Mode
from homeassistant.components.vacuum import (
    STATE_CLEANING,
    STATE_DOCKED,
    STATE_RETURNING,
)
from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_DISARMED,
    STATE_ALARM_TRIGGERED,
    STATE_IDLE,
    STATE_PAUSED,
    Platform,
)

DOMAIN = "tuya_ce"

DEVICE_CONFIG_MANAGER = "device_config_manager"

STORAGE_VERSION = 1
SERVICE_UPDATE_REMOTE_CONFIGURATION = "update_remote_configuration"

BASE_URL = "https://raw.githubusercontent.com/elad-bar/ha-tuya-ce/main/config/"

DEVICES_CONFIG = "devices"
COUNTRIES_CONFIG = "countries"
UNITS_CONFIG = "units"

TUYA_CONFIGURATIONS = [
    DEVICES_CONFIG,
    COUNTRIES_CONFIG,
    UNITS_CONFIG
]

CONF_AUTH_TYPE = "auth_type"
CONF_PROJECT_TYPE = "tuya_project_type"
CONF_ENDPOINT = "endpoint"
CONF_ACCESS_ID = "access_id"
CONF_ACCESS_SECRET = "access_secret"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_COUNTRY_CODE = "country_code"
CONF_APP_TYPE = "tuya_app_type"

TUYA_DISCOVERY_NEW = "tuya_discovery_new"
TUYA_HA_SIGNAL_UPDATE_ENTITY = "tuya_entry_update"

TUYA_RESPONSE_CODE = "code"
TUYA_RESPONSE_RESULT = "result"
TUYA_RESPONSE_MSG = "msg"
TUYA_RESPONSE_SUCCESS = "success"
TUYA_RESPONSE_PLATFORM_URL = "platform_url"

TUYA_SMART_APP = "tuyaSmart"
SMART_LIFE_APP = "smartlife"

ELECTRIC_RESISTANCE_OHM = "Ω"

PLATFORMS = [
    Platform.ALARM_CONTROL_PANEL,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.CAMERA,
    Platform.CLIMATE,
    Platform.COVER,
    Platform.FAN,
    Platform.HUMIDIFIER,
    Platform.LIGHT,
    Platform.NUMBER,
    Platform.SCENE,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SIREN,
    Platform.SWITCH,
    Platform.VACUUM,
]

TUYA_MODE_RETURN_HOME = "chargego"
TUYA_STATUS_TO_HA = {
    "charge_done": STATE_DOCKED,
    "chargecompleted": STATE_DOCKED,
    "chargego": STATE_DOCKED,
    "charging": STATE_DOCKED,
    "cleaning": STATE_CLEANING,
    "docking": STATE_RETURNING,
    "goto_charge": STATE_RETURNING,
    "goto_pos": STATE_CLEANING,
    "mop_clean": STATE_CLEANING,
    "part_clean": STATE_CLEANING,
    "paused": STATE_PAUSED,
    "pick_zone_clean": STATE_CLEANING,
    "pos_arrived": STATE_CLEANING,
    "pos_unarrive": STATE_CLEANING,
    "random": STATE_CLEANING,
    "sleep": STATE_IDLE,
    "smart_clean": STATE_CLEANING,
    "smart": STATE_CLEANING,
    "spot_clean": STATE_CLEANING,
    "standby": STATE_IDLE,
    "wall_clean": STATE_CLEANING,
    "wall_follow": STATE_CLEANING,
    "zone_clean": STATE_CLEANING,
}

TUYA_HVAC_TO_HA = {
    "auto": HVACMode.HEAT_COOL,
    "cold": HVACMode.COOL,
    "freeze": HVACMode.COOL,
    "heat": HVACMode.HEAT,
    "hot": HVACMode.HEAT,
    "manual": HVACMode.HEAT_COOL,
    "wet": HVACMode.DRY,
    "wind": HVACMode.FAN_ONLY,
}

TUYA_SPECIAL_MAPPING = {
    "infrared_ac": {
        "F": "wind",
        "M": "mode",
        "T": "temp"
    }
}

TUYA_RELATED_DOMAINS = {
    "sensor": ["binary_sensor"],
    "select": ["binary_sensor", "sensor"]
}

TUYA_TYPES_MAPPING = {
    "ro_boolean": "binary_sensor",
    "rw_boolean": "switch",

    "ro_integer": "sensor",
    "rw_integer": "number",

    "ro_string": "sensor",
    "rw_string": "select",

    "ro_enum": "sensor",
    "rw_enum": "select",

    "ro_json": "sensor",
    "rw_json": "select"
}

ACCESS_MODES = {
    True: "ro",
    False: "rw"
}

TUYA_UNSUPPORTED_CATEGORIES_DATA_KEYS = ["name", "model", "product_name"]

STATE_MAPPING: dict[str, str] = {
    Mode.DISARMED: STATE_ALARM_DISARMED,
    Mode.ARM: STATE_ALARM_ARMED_AWAY,
    Mode.HOME: STATE_ALARM_ARMED_HOME,
    Mode.SOS: STATE_ALARM_TRIGGERED,
}

WEATHER_CONDITION = "tuya_ce__weather_condition"

PLATFORM_FIELDS = {
    Platform.ALARM_CONTROL_PANEL: ["name"],
    Platform.BINARY_SENSOR: ["dpcode", "name", "icon", "on_value",
                             "device_class", "entity_category"],
    Platform.BUTTON: ["name", "icon", "entity_category"],
    Platform.CLIMATE: ["switch_only_hvac_mode"],
    Platform.COVER: ["name", "current_state", "current_position", "current_position",
                     "set_position", "device_class", "open_instruction_value", "close_instruction_value",
                     "stop_instruction_value"],
    Platform.HUMIDIFIER: ["dpcode", "humidity", "device_class"],
    Platform.LIGHT: ["name", "brightness", "brightness_max", "brightness_min",
                     "device_class", "color_mode", "color_temp", "entity_category",
                     "default_color_type", "color_data"],
    Platform.NUMBER: ["name", "device_class", "entity_category", "icon",
                      "native_unit_of_measurement"],
    Platform.SELECT: ["name", "entity_category", "icon", "translation_key"],
    Platform.SENSOR: ["name", "device_class", "state_class", "entity_category",
                      "icon", "native_unit_of_measurement", "entity_registry_enabled_default", "subkey",
                      "translation_key"],
    Platform.SIREN: ["name"],
    Platform.SWITCH: ["name", "icon", "entity_category", "device_class"]
}
