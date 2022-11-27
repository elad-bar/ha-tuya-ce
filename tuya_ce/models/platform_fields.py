from dataclasses import dataclass


@dataclass
class PlatformFields:
    """Tuya specific device classes, used for translations."""
    ALARM_CONTROL_PANEL = ["name"]

    BINARY_SENSOR = ["dpcode", "name", "icon", "on_value",
                     "device_class",  "entity_category"]

    BUTTON = ["name", "icon", "entity_category"]

    CLIMATE = ["switch_only_hvac_mode"]

    COVER = ["name", "current_state", "current_position", "current_position",
             "set_position", "device_class", "open_instruction_value", "close_instruction_value",
             "stop_instruction_value"]

    HUMIDIFIER = ["dpcode", "humidity", "device_class"]

    LIGHT = ["name", "brightness", "brightness_max", "brightness_min",
             "device_class", "color_mode", "color_temp", "entity_category",
             "default_color_type", "color_data"]

    NUMBER = ["name", "device_class", "entity_category", "icon",
              "native_unit_of_measurement"]

    SELECT = ["name", "device_class", "entity_category", "icon"]

    SENSOR = ["name", "device_class", "state_class", "entity_category",
              "icon", "native_unit_of_measurement", "entity_registry_enabled_default", "subkey"]

    SIREN = ["name"]

    SWITCH = ["name", "icon", "entity_category", "device_class"]
