from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntityDescription,
)
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.button import ButtonEntityDescription
from homeassistant.components.climate import HVACMode
from homeassistant.components.cover import CoverDeviceClass
from homeassistant.components.humidifier import HumidifierDeviceClass
from homeassistant.components.number import NumberDeviceClass, NumberEntityDescription
from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.components.siren import SirenEntityDescription
from homeassistant.components.switch import SwitchDeviceClass, SwitchEntityDescription
from homeassistant.const import (
    ELECTRIC_CURRENT_AMPERE,
    ELECTRIC_POTENTIAL_VOLT,
    PERCENTAGE,
    POWER_KILO_WATT,
    TIME_MINUTES,
)
from homeassistant.helpers.entity import EntityCategory

from .enums.tuya_device_class import TuyaDeviceClass
from ..models.color_type_data import ColorTypes
from ..models.tuya_entity_descriptors import (
    TuyaBinarySensorEntityDescription,
    TuyaClimateEntityDescription,
    TuyaCoverEntityDescription,
    TuyaHumidifierEntityDescription,
    TuyaLightEntityDescription,
    TuyaSensorEntityDescription,
)
from .enums.dp_code import DPCode

# All descriptions can be found here:
# https://developer.tuya.com/en/docs/iot/standarddescription?id=K9i5ql6waswzq
ALARM: dict[str, tuple[AlarmControlPanelEntityDescription, ...]] = {
    # Alarm Host
    # https://developer.tuya.com/en/docs/iot/categorymal?id=Kaiuz33clqxaf
    "mal": (
        AlarmControlPanelEntityDescription(
            key=DPCode.MASTER_MODE,
            name="Alarm",
        ),
    )
}


# Commonly used sensors
TAMPER_BINARY_SENSOR = TuyaBinarySensorEntityDescription(
    key=DPCode.TEMPER_ALARM,
    name="Tamper",
    device_class=BinarySensorDeviceClass.TAMPER,
    entity_category=EntityCategory.DIAGNOSTIC,
)


# All descriptions can be found here. Mostly the Boolean data types in the
# default status set of each category (that don't have a set instruction)
# end up being a binary sensor.
# https://developer.tuya.com/en/docs/iot/standarddescription?id=K9i5ql6waswzq
BINARY_SENSORS: dict[str, tuple[TuyaBinarySensorEntityDescription, ...]] = {
    # Multi-functional Sensor
    # https://developer.tuya.com/en/docs/iot/categorydgnbj?id=Kaiuz3yorvzg3
    "dgnbj": (
        TuyaBinarySensorEntityDescription(
            key=DPCode.GAS_SENSOR_STATE,
            name="Gas",
            icon="mdi:gas-cylinder",
            device_class=BinarySensorDeviceClass.SAFETY,
            on_value="alarm",
        ),
        TuyaBinarySensorEntityDescription(
            key=DPCode.CH4_SENSOR_STATE,
            name="Methane",
            device_class=BinarySensorDeviceClass.GAS,
            on_value="alarm",
        ),
        TuyaBinarySensorEntityDescription(
            key=DPCode.VOC_STATE,
            name="Volatile organic compound",
            device_class=BinarySensorDeviceClass.SAFETY,
            on_value="alarm",
        ),
        TuyaBinarySensorEntityDescription(
            key=DPCode.PM25_STATE,
            name="Particulate matter 2.5 µm",
            device_class=BinarySensorDeviceClass.SAFETY,
            on_value="alarm",
        ),
        TuyaBinarySensorEntityDescription(
            key=DPCode.CO_STATE,
            name="Carbon monoxide",
            icon="mdi:molecule-co",
            device_class=BinarySensorDeviceClass.SAFETY,
            on_value="alarm",
        ),
        TuyaBinarySensorEntityDescription(
            key=DPCode.CO2_STATE,
            icon="mdi:molecule-co2",
            name="Carbon dioxide",
            device_class=BinarySensorDeviceClass.SAFETY,
            on_value="alarm",
        ),
        TuyaBinarySensorEntityDescription(
            key=DPCode.CH2O_STATE,
            name="Formaldehyde",
            device_class=BinarySensorDeviceClass.SAFETY,
            on_value="alarm",
        ),
        TuyaBinarySensorEntityDescription(
            key=DPCode.DOORCONTACT_STATE,
            name="Door",
            device_class=BinarySensorDeviceClass.DOOR,
        ),
        TuyaBinarySensorEntityDescription(
            key=DPCode.WATERSENSOR_STATE,
            name="Water leak",
            device_class=BinarySensorDeviceClass.MOISTURE,
            on_value="alarm",
        ),
        TuyaBinarySensorEntityDescription(
            key=DPCode.PRESSURE_STATE,
            name="Pressure",
            on_value="alarm",
        ),
        TuyaBinarySensorEntityDescription(
            key=DPCode.SMOKE_SENSOR_STATE,
            name="Smoke",
            icon="mdi:smoke-detector",
            device_class=BinarySensorDeviceClass.SMOKE,
            on_value="alarm",
        ),
        TAMPER_BINARY_SENSOR,
    ),
    # CO2 Detector
    # https://developer.tuya.com/en/docs/iot/categoryco2bj?id=Kaiuz3wes7yuy
    "co2bj": (
        TuyaBinarySensorEntityDescription(
            key=DPCode.CO2_STATE,
            device_class=BinarySensorDeviceClass.SAFETY,
            on_value="alarm",
        ),
        TAMPER_BINARY_SENSOR,
    ),
    # CO Detector
    # https://developer.tuya.com/en/docs/iot/categorycobj?id=Kaiuz3u1j6q1v
    "cobj": (
        TuyaBinarySensorEntityDescription(
            key=DPCode.CO_STATE,
            device_class=BinarySensorDeviceClass.SAFETY,
            on_value="1",
        ),
        TuyaBinarySensorEntityDescription(
            key=DPCode.CO_STATUS,
            device_class=BinarySensorDeviceClass.SAFETY,
            on_value="alarm",
        ),
        TAMPER_BINARY_SENSOR,
    ),
    # Smart Pet Feeder
    # https://developer.tuya.com/en/docs/iot/categorycwwsq?id=Kaiuz2b6vydld
    "cwwsq": (
        TuyaBinarySensorEntityDescription(
            key=DPCode.FEED_STATE,
            name="Feeding",
            icon="mdi:information",
            on_value="feeding",
        ),
    ),
    # Human Presence Sensor
    # https://developer.tuya.com/en/docs/iot/categoryhps?id=Kaiuz42yhn1hs
    "hps": (
        TuyaBinarySensorEntityDescription(
            key=DPCode.PRESENCE_STATE,
            device_class=BinarySensorDeviceClass.MOTION,
            on_value="presence",
        ),
    ),
    # Formaldehyde Detector
    # Note: Not documented
    "jqbj": (
        TuyaBinarySensorEntityDescription(
            key=DPCode.CH2O_STATE,
            device_class=BinarySensorDeviceClass.SAFETY,
            on_value="alarm",
        ),
        TAMPER_BINARY_SENSOR,
    ),
    # Methane Detector
    # https://developer.tuya.com/en/docs/iot/categoryjwbj?id=Kaiuz40u98lkm
    "jwbj": (
        TuyaBinarySensorEntityDescription(
            key=DPCode.CH4_SENSOR_STATE,
            device_class=BinarySensorDeviceClass.GAS,
            on_value="alarm",
        ),
        TAMPER_BINARY_SENSOR,
    ),
    # Door and Window Controller
    # https://developer.tuya.com/en/docs/iot/s?id=K9gf48r5zjsy9
    "mc": (
        TuyaBinarySensorEntityDescription(
            key=DPCode.STATUS,
            device_class=BinarySensorDeviceClass.DOOR,
            on_value={"open", "opened"},
        ),
    ),
    # Door Window Sensor
    # https://developer.tuya.com/en/docs/iot/s?id=K9gf48hm02l8m
    "mcs": (
        TuyaBinarySensorEntityDescription(
            key=DPCode.DOORCONTACT_STATE,
            device_class=BinarySensorDeviceClass.DOOR,
        ),
        TAMPER_BINARY_SENSOR,
    ),
    # Access Control
    # https://developer.tuya.com/en/docs/iot/s?id=Kb0o2xhlkxbet
    "mk": (
        TuyaBinarySensorEntityDescription(
            key=DPCode.CLOSED_OPENED_KIT,
            device_class=BinarySensorDeviceClass.LOCK,
            on_value={"AQAB"},
        ),
    ),
    # Luminance Sensor
    # https://developer.tuya.com/en/docs/iot/categoryldcg?id=Kaiuz3n7u69l8
    "ldcg": (
        TuyaBinarySensorEntityDescription(
            key=DPCode.TEMPER_ALARM,
            name="Tamper",
            device_class=BinarySensorDeviceClass.TAMPER,
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        TAMPER_BINARY_SENSOR,
    ),
    # PIR Detector
    # https://developer.tuya.com/en/docs/iot/categorypir?id=Kaiuz3ss11b80
    "pir": (
        TuyaBinarySensorEntityDescription(
            key=DPCode.PIR,
            device_class=BinarySensorDeviceClass.MOTION,
            on_value="pir",
        ),
        TAMPER_BINARY_SENSOR,
    ),
    # PM2.5 Sensor
    # https://developer.tuya.com/en/docs/iot/categorypm25?id=Kaiuz3qof3yfu
    "pm2.5": (
        TuyaBinarySensorEntityDescription(
            key=DPCode.PM25_STATE,
            device_class=BinarySensorDeviceClass.SAFETY,
            on_value="alarm",
        ),
        TAMPER_BINARY_SENSOR,
    ),
    # Gas Detector
    # https://developer.tuya.com/en/docs/iot/categoryrqbj?id=Kaiuz3d162ubw
    "rqbj": (
        TuyaBinarySensorEntityDescription(
            key=DPCode.GAS_SENSOR_STATUS,
            device_class=BinarySensorDeviceClass.GAS,
            on_value="alarm",
        ),
        TuyaBinarySensorEntityDescription(
            key=DPCode.GAS_SENSOR_STATE,
            device_class=BinarySensorDeviceClass.GAS,
            on_value="1",
        ),
        TAMPER_BINARY_SENSOR,
    ),
    # Water Detector
    # https://developer.tuya.com/en/docs/iot/categorysj?id=Kaiuz3iub2sli
    "sj": (
        TuyaBinarySensorEntityDescription(
            key=DPCode.WATERSENSOR_STATE,
            device_class=BinarySensorDeviceClass.MOISTURE,
            on_value="alarm",
        ),
        TAMPER_BINARY_SENSOR,
    ),
    # Emergency Button
    # https://developer.tuya.com/en/docs/iot/categorysos?id=Kaiuz3oi6agjy
    "sos": (
        TuyaBinarySensorEntityDescription(
            key=DPCode.SOS_STATE,
            device_class=BinarySensorDeviceClass.SAFETY,
        ),
        TAMPER_BINARY_SENSOR,
    ),
    # Volatile Organic Compound Sensor
    # Note: Undocumented in cloud API docs, based on test device
    "voc": (
        TuyaBinarySensorEntityDescription(
            key=DPCode.VOC_STATE,
            device_class=BinarySensorDeviceClass.SAFETY,
            on_value="alarm",
        ),
        TAMPER_BINARY_SENSOR,
    ),
    # Thermostatic Radiator Valve
    # Not documented
    "wkf": (
        TuyaBinarySensorEntityDescription(
            key=DPCode.WINDOW_STATE,
            name="Window",
            device_class=BinarySensorDeviceClass.WINDOW,
            on_value="opened",
        ),
    ),
    # Temperature and Humidity Sensor
    # https://developer.tuya.com/en/docs/iot/categorywsdcg?id=Kaiuz3hinij34
    "wsdcg": (TAMPER_BINARY_SENSOR,),
    # Pressure Sensor
    # https://developer.tuya.com/en/docs/iot/categoryylcg?id=Kaiuz3kc2e4gm
    "ylcg": (
        TuyaBinarySensorEntityDescription(
            key=DPCode.PRESSURE_STATE,
            on_value="alarm",
        ),
        TAMPER_BINARY_SENSOR,
    ),
    # Smoke Detector
    # https://developer.tuya.com/en/docs/iot/categoryywbj?id=Kaiuz3f6sf952
    "ywbj": (
        TuyaBinarySensorEntityDescription(
            key=DPCode.SMOKE_SENSOR_STATUS,
            device_class=BinarySensorDeviceClass.SMOKE,
            on_value="alarm",
        ),
        TuyaBinarySensorEntityDescription(
            key=DPCode.SMOKE_SENSOR_STATE,
            device_class=BinarySensorDeviceClass.SMOKE,
            on_value="1",
        ),
        TAMPER_BINARY_SENSOR,
    ),
    # Vibration Sensor
    # https://developer.tuya.com/en/docs/iot/categoryzd?id=Kaiuz3a5vrzno
    "zd": (
        TuyaBinarySensorEntityDescription(
            key=f"{DPCode.SHOCK_STATE}_vibration",
            dpcode=DPCode.SHOCK_STATE,
            name="Vibration",
            device_class=BinarySensorDeviceClass.VIBRATION,
            on_value="vibration",
        ),
        TuyaBinarySensorEntityDescription(
            key=f"{DPCode.SHOCK_STATE}_drop",
            dpcode=DPCode.SHOCK_STATE,
            name="Drop",
            icon="mdi:icon=package-down",
            on_value="drop",
        ),
        TuyaBinarySensorEntityDescription(
            key=f"{DPCode.SHOCK_STATE}_tilt",
            dpcode=DPCode.SHOCK_STATE,
            name="Tilt",
            icon="mdi:spirit-level",
            on_value="tilt",
        ),
    ),
}

# All descriptions can be found here.
# https://developer.tuya.com/en/docs/iot/standarddescription?id=K9i5ql6waswzq
BUTTONS: dict[str, tuple[ButtonEntityDescription, ...]] = {
    # Robot Vacuum
    # https://developer.tuya.com/en/docs/iot/fsd?id=K9gf487ck1tlo
    "sd": (
        ButtonEntityDescription(
            key=DPCode.RESET_DUSTER_CLOTH,
            name="Reset duster cloth",
            icon="mdi:restart",
            entity_category=EntityCategory.CONFIG,
        ),
        ButtonEntityDescription(
            key=DPCode.RESET_EDGE_BRUSH,
            name="Reset edge brush",
            icon="mdi:restart",
            entity_category=EntityCategory.CONFIG,
        ),
        ButtonEntityDescription(
            key=DPCode.RESET_FILTER,
            name="Reset filter",
            icon="mdi:air-filter",
            entity_category=EntityCategory.CONFIG,
        ),
        ButtonEntityDescription(
            key=DPCode.RESET_MAP,
            name="Reset map",
            icon="mdi:map-marker-remove",
            entity_category=EntityCategory.CONFIG,
        ),
        ButtonEntityDescription(
            key=DPCode.RESET_ROLL_BRUSH,
            name="Reset roll brush",
            icon="mdi:restart",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Wake Up Light II
    # Not documented
    "hxd": (
        ButtonEntityDescription(
            key=DPCode.SWITCH_USB6,
            name="Snooze",
            icon="mdi:sleep",
        ),
    ),
}

# All descriptions can be found here:
# https://developer.tuya.com/en/docs/iot/standarddescription?id=K9i5ql6waswzq
CAMERAS: tuple[str, ...] = (
    # Smart Camera (including doorbells)
    # https://developer.tuya.com/en/docs/iot/categorysgbj?id=Kaiuz37tlpbnu
    "sp",
)

CLIMATE_DESCRIPTIONS: dict[str, TuyaClimateEntityDescription] = {
    # Air conditioner
    # https://developer.tuya.com/en/docs/iot/categorykt?id=Kaiuz0z71ov2n
    "kt": TuyaClimateEntityDescription(
        key="kt",
        switch_only_hvac_mode=HVACMode.COOL,
    ),
    # Heater
    # https://developer.tuya.com/en/docs/iot/f?id=K9gf46epy4j82
    "qn": TuyaClimateEntityDescription(
        key="qn",
        switch_only_hvac_mode=HVACMode.HEAT,
    ),
    # Heater
    # https://developer.tuya.com/en/docs/iot/categoryrs?id=Kaiuz0nfferyx
    "rs": TuyaClimateEntityDescription(
        key="rs",
        switch_only_hvac_mode=HVACMode.HEAT,
    ),
    # Thermostat
    # https://developer.tuya.com/en/docs/iot/f?id=K9gf45ld5l0t9
    "wk": TuyaClimateEntityDescription(
        key="wk",
        switch_only_hvac_mode=HVACMode.HEAT_COOL,
    ),
    # Thermostatic Radiator Valve
    # Not documented
    "wkf": TuyaClimateEntityDescription(
        key="wkf",
        switch_only_hvac_mode=HVACMode.HEAT,
    ),
}

COVERS: dict[str, tuple[TuyaCoverEntityDescription, ...]] = {
    # Curtain
    # Note: Multiple curtains isn't documented
    # https://developer.tuya.com/en/docs/iot/categorycl?id=Kaiuz1hnpo7df
    "cl": (
        TuyaCoverEntityDescription(
            key=DPCode.CONTROL,
            name="Curtain",
            current_state=DPCode.SITUATION_SET,
            current_position=(DPCode.PERCENT_CONTROL, DPCode.PERCENT_STATE),
            set_position=DPCode.PERCENT_CONTROL,
            device_class=CoverDeviceClass.CURTAIN,
        ),
        TuyaCoverEntityDescription(
            key=DPCode.CONTROL_2,
            name="Curtain 2",
            current_position=DPCode.PERCENT_STATE_2,
            set_position=DPCode.PERCENT_CONTROL_2,
            device_class=CoverDeviceClass.CURTAIN,
        ),
        TuyaCoverEntityDescription(
            key=DPCode.CONTROL_3,
            name="Curtain 3",
            current_position=DPCode.PERCENT_STATE_3,
            set_position=DPCode.PERCENT_CONTROL_3,
            device_class=CoverDeviceClass.CURTAIN,
        ),
        TuyaCoverEntityDescription(
            key=DPCode.MACH_OPERATE,
            name="Curtain",
            current_position=DPCode.POSITION,
            set_position=DPCode.POSITION,
            device_class=CoverDeviceClass.CURTAIN,
            open_instruction_value="FZ",
            close_instruction_value="ZZ",
            stop_instruction_value="STOP",
        ),
        # switch_1 is an undocumented code that behaves identically to control
        # It is used by the Kogan Smart Blinds Driver
        TuyaCoverEntityDescription(
            key=DPCode.SWITCH_1,
            name="Blind",
            current_position=DPCode.PERCENT_CONTROL,
            set_position=DPCode.PERCENT_CONTROL,
            device_class=CoverDeviceClass.BLIND,
        ),
    ),
    # Garage Door Opener
    # https://developer.tuya.com/en/docs/iot/categoryckmkzq?id=Kaiuz0ipcboee
    "ckmkzq": (
        TuyaCoverEntityDescription(
            key=DPCode.SWITCH_1,
            name="Door",
            current_state=DPCode.DOORCONTACT_STATE,
            current_state_inverse=True,
            device_class=CoverDeviceClass.GARAGE,
        ),
        TuyaCoverEntityDescription(
            key=DPCode.SWITCH_2,
            name="Door 2",
            current_state=DPCode.DOORCONTACT_STATE_2,
            current_state_inverse=True,
            device_class=CoverDeviceClass.GARAGE,
        ),
        TuyaCoverEntityDescription(
            key=DPCode.SWITCH_3,
            name="Door 3",
            current_state=DPCode.DOORCONTACT_STATE_3,
            current_state_inverse=True,
            device_class=CoverDeviceClass.GARAGE,
        ),
    ),
    # Curtain Switch
    # https://developer.tuya.com/en/docs/iot/category-clkg?id=Kaiuz0gitil39
    "clkg": (
        TuyaCoverEntityDescription(
            key=DPCode.CONTROL,
            name="Curtain",
            current_position=DPCode.PERCENT_CONTROL,
            set_position=DPCode.PERCENT_CONTROL,
            device_class=CoverDeviceClass.CURTAIN,
        ),
        TuyaCoverEntityDescription(
            key=DPCode.CONTROL_2,
            name="Curtain 2",
            current_position=DPCode.PERCENT_CONTROL_2,
            set_position=DPCode.PERCENT_CONTROL_2,
            device_class=CoverDeviceClass.CURTAIN,
        ),
    ),
    # Curtain Robot
    # Note: Not documented
    "jdcljqr": (
        TuyaCoverEntityDescription(
            key=DPCode.CONTROL,
            current_position=DPCode.PERCENT_STATE,
            set_position=DPCode.PERCENT_CONTROL,
            device_class=CoverDeviceClass.CURTAIN,
        ),
    ),
}


TUYA_SUPPORT_TYPE = {
    "fs",  # Fan
    "fsd",  # Fan with Light
    "fskg",  # Fan wall switch
    "kj",  # Air Purifier
}

HUMIDIFIERS: dict[str, TuyaHumidifierEntityDescription] = {
    # Dehumidifier
    # https://developer.tuya.com/en/docs/iot/categorycs?id=Kaiuz1vcz4dha
    "cs": TuyaHumidifierEntityDescription(
        key=DPCode.SWITCH,
        dpcode=(DPCode.SWITCH, DPCode.SWITCH_SPRAY),
        humidity=DPCode.DEHUMIDITY_SET_VALUE,
        device_class=HumidifierDeviceClass.DEHUMIDIFIER,
    ),
    # Humidifier
    # https://developer.tuya.com/en/docs/iot/categoryjsq?id=Kaiuz1smr440b
    "jsq": TuyaHumidifierEntityDescription(
        key=DPCode.SWITCH,
        dpcode=(DPCode.SWITCH, DPCode.SWITCH_SPRAY),
        humidity=DPCode.HUMIDITY_SET,
        device_class=HumidifierDeviceClass.HUMIDIFIER,
    ),
}


LIGHTS: dict[str, tuple[TuyaLightEntityDescription, ...]] = {
    # Curtain Switch
    # https://developer.tuya.com/en/docs/iot/category-clkg?id=Kaiuz0gitil39
    "clkg": (
        TuyaLightEntityDescription(
            key=DPCode.SWITCH_BACKLIGHT,
            name="Backlight",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # String Lights
    # https://developer.tuya.com/en/docs/iot/dc?id=Kaof7taxmvadu
    "dc": (
        TuyaLightEntityDescription(
            key=DPCode.SWITCH_LED,
            color_mode=DPCode.WORK_MODE,
            brightness=DPCode.BRIGHT_VALUE,
            color_temp=DPCode.TEMP_VALUE,
            color_data=DPCode.COLOUR_DATA,
        ),
    ),
    # Strip Lights
    # https://developer.tuya.com/en/docs/iot/dd?id=Kaof804aibg2l
    "dd": (
        TuyaLightEntityDescription(
            key=DPCode.SWITCH_LED,
            color_mode=DPCode.WORK_MODE,
            brightness=DPCode.BRIGHT_VALUE,
            color_temp=DPCode.TEMP_VALUE,
            color_data=DPCode.COLOUR_DATA,
            default_color_type=ColorTypes().v2,
        ),
    ),
    # Light
    # https://developer.tuya.com/en/docs/iot/categorydj?id=Kaiuyzy3eheyy
    "dj": (
        TuyaLightEntityDescription(
            key=DPCode.SWITCH_LED,
            color_mode=DPCode.WORK_MODE,
            brightness=(DPCode.BRIGHT_VALUE_V2, DPCode.BRIGHT_VALUE),
            color_temp=(DPCode.TEMP_VALUE_V2, DPCode.TEMP_VALUE),
            color_data=(DPCode.COLOUR_DATA_V2, DPCode.COLOUR_DATA),
        ),
        # Not documented
        # Based on multiple reports: manufacturer customized Dimmer 2 switches
        TuyaLightEntityDescription(
            key=DPCode.SWITCH_1,
            name="Light",
            brightness=DPCode.BRIGHT_VALUE_1,
        ),
    ),
    # Ceiling Fan Light
    # https://developer.tuya.com/en/docs/iot/fsd?id=Kaof8eiei4c2v
    "fsd": (
        TuyaLightEntityDescription(
            key=DPCode.SWITCH_LED,
            color_mode=DPCode.WORK_MODE,
            brightness=DPCode.BRIGHT_VALUE,
            color_temp=DPCode.TEMP_VALUE,
            color_data=DPCode.COLOUR_DATA,
        ),
    ),
    # Ambient Light
    # https://developer.tuya.com/en/docs/iot/ambient-light?id=Kaiuz06amhe6g
    "fwd": (
        TuyaLightEntityDescription(
            key=DPCode.SWITCH_LED,
            color_mode=DPCode.WORK_MODE,
            brightness=DPCode.BRIGHT_VALUE,
            color_temp=DPCode.TEMP_VALUE,
            color_data=DPCode.COLOUR_DATA,
        ),
    ),
    # Motion Sensor Light
    # https://developer.tuya.com/en/docs/iot/gyd?id=Kaof8a8hycfmy
    "gyd": (
        TuyaLightEntityDescription(
            key=DPCode.SWITCH_LED,
            color_mode=DPCode.WORK_MODE,
            brightness=DPCode.BRIGHT_VALUE,
            color_temp=DPCode.TEMP_VALUE,
            color_data=DPCode.COLOUR_DATA,
        ),
    ),
    # Humidifier Light
    # https://developer.tuya.com/en/docs/iot/categoryjsq?id=Kaiuz1smr440b
    "jsq": (
        TuyaLightEntityDescription(
            key=DPCode.SWITCH_LED,
            color_mode=DPCode.WORK_MODE,
            brightness=DPCode.BRIGHT_VALUE,
            color_data=DPCode.COLOUR_DATA_HSV,
        ),
    ),
    # Switch
    # https://developer.tuya.com/en/docs/iot/s?id=K9gf7o5prgf7s
    "kg": (
        TuyaLightEntityDescription(
            key=DPCode.SWITCH_BACKLIGHT,
            name="Backlight",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Air conditioner
    # https://developer.tuya.com/en/docs/iot/categorykt?id=Kaiuz0z71ov2n
    "kt": (
        TuyaLightEntityDescription(
            key=DPCode.LIGHT,
            name="Backlight",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Unknown light product
    # Found as VECINO RGBW as provided by diagnostics
    # Not documented
    "mbd": (
        TuyaLightEntityDescription(
            key=DPCode.SWITCH_LED,
            color_mode=DPCode.WORK_MODE,
            brightness=DPCode.BRIGHT_VALUE,
            color_data=DPCode.COLOUR_DATA,
        ),
    ),
    # Unknown product with light capabilities
    # Fond in some diffusers, plugs and PIR flood lights
    # Not documented
    "qjdcz": (
        TuyaLightEntityDescription(
            key=DPCode.SWITCH_LED,
            color_mode=DPCode.WORK_MODE,
            brightness=DPCode.BRIGHT_VALUE,
            color_data=DPCode.COLOUR_DATA,
        ),
    ),
    # Heater
    # https://developer.tuya.com/en/docs/iot/categoryqn?id=Kaiuz18kih0sm
    "qn": (
        TuyaLightEntityDescription(
            key=DPCode.LIGHT,
            name="Backlight",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Smart Camera
    # https://developer.tuya.com/en/docs/iot/categorysp?id=Kaiuz35leyo12
    "sp": (
        TuyaLightEntityDescription(
            key=DPCode.FLOODLIGHT_SWITCH,
            brightness=DPCode.FLOODLIGHT_LIGHTNESS,
            name="Floodlight",
        ),
        TuyaLightEntityDescription(
            key=DPCode.BASIC_INDICATOR,
            name="Indicator Light",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Dimmer Switch
    # https://developer.tuya.com/en/docs/iot/categorytgkg?id=Kaiuz0ktx7m0o
    "tgkg": (
        TuyaLightEntityDescription(
            key=DPCode.SWITCH_LED_1,
            name="Light",
            brightness=DPCode.BRIGHT_VALUE_1,
            brightness_max=DPCode.BRIGHTNESS_MAX_1,
            brightness_min=DPCode.BRIGHTNESS_MIN_1,
        ),
        TuyaLightEntityDescription(
            key=DPCode.SWITCH_LED_2,
            name="Light 2",
            brightness=DPCode.BRIGHT_VALUE_2,
            brightness_max=DPCode.BRIGHTNESS_MAX_2,
            brightness_min=DPCode.BRIGHTNESS_MIN_2,
        ),
        TuyaLightEntityDescription(
            key=DPCode.SWITCH_LED_3,
            name="Light 3",
            brightness=DPCode.BRIGHT_VALUE_3,
            brightness_max=DPCode.BRIGHTNESS_MAX_3,
            brightness_min=DPCode.BRIGHTNESS_MIN_3,
        ),
    ),
    # Dimmer
    # https://developer.tuya.com/en/docs/iot/tgq?id=Kaof8ke9il4k4
    "tgq": (
        TuyaLightEntityDescription(
            key=DPCode.SWITCH_LED,
            name="Light",
            brightness=(DPCode.BRIGHT_VALUE_V2, DPCode.BRIGHT_VALUE),
            brightness_max=DPCode.BRIGHTNESS_MAX_1,
            brightness_min=DPCode.BRIGHTNESS_MIN_1,
        ),
        TuyaLightEntityDescription(
            key=DPCode.SWITCH_LED_1,
            name="Light",
            brightness=DPCode.BRIGHT_VALUE_1,
        ),
        TuyaLightEntityDescription(
            key=DPCode.SWITCH_LED_2,
            name="Light 2",
            brightness=DPCode.BRIGHT_VALUE_2,
        ),
    ),
    # Wake Up Light II
    # Not documented
    "hxd": (
        TuyaLightEntityDescription(
            key=DPCode.SWITCH_LED,
            name="Light",
            brightness=(DPCode.BRIGHT_VALUE_V2, DPCode.BRIGHT_VALUE),
            brightness_max=DPCode.BRIGHTNESS_MAX_1,
            brightness_min=DPCode.BRIGHTNESS_MIN_1,
        ),
    ),
    # Solar Light
    # https://developer.tuya.com/en/docs/iot/tynd?id=Kaof8j02e1t98
    "tyndj": (
        TuyaLightEntityDescription(
            key=DPCode.SWITCH_LED,
            color_mode=DPCode.WORK_MODE,
            brightness=DPCode.BRIGHT_VALUE,
            color_temp=DPCode.TEMP_VALUE,
            color_data=DPCode.COLOUR_DATA,
        ),
    ),
    # Ceiling Light
    # https://developer.tuya.com/en/docs/iot/ceiling-light?id=Kaiuz03xxfc4r
    "xdd": (
        TuyaLightEntityDescription(
            key=DPCode.SWITCH_LED,
            color_mode=DPCode.WORK_MODE,
            brightness=DPCode.BRIGHT_VALUE,
            color_temp=DPCode.TEMP_VALUE,
            color_data=DPCode.COLOUR_DATA,
        ),
        TuyaLightEntityDescription(
            key=DPCode.SWITCH_NIGHT_LIGHT,
            name="Night light",
        ),
    ),
    # Remote Control
    # https://developer.tuya.com/en/docs/iot/ykq?id=Kaof8ljn81aov
    "ykq": (
        TuyaLightEntityDescription(
            key=DPCode.SWITCH_CONTROLLER,
            color_mode=DPCode.WORK_MODE,
            brightness=DPCode.BRIGHT_CONTROLLER,
            color_temp=DPCode.TEMP_CONTROLLER,
        ),
    ),
    # Fan
    # https://developer.tuya.com/en/docs/iot/categoryfs?id=Kaiuz1xweel1c
    "fs": (
        TuyaLightEntityDescription(
            key=DPCode.LIGHT,
            color_mode=DPCode.WORK_MODE,
            brightness=DPCode.BRIGHT_VALUE,
            color_temp=DPCode.TEMP_VALUE,
        ),
    ),
}

# Socket (duplicate of `kg`)
# https://developer.tuya.com/en/docs/iot/s?id=K9gf7o5prgf7s
LIGHTS["cz"] = LIGHTS["kg"]

# Power Socket (duplicate of `kg`)
# https://developer.tuya.com/en/docs/iot/s?id=K9gf7o5prgf7s
LIGHTS["pc"] = LIGHTS["kg"]


# All descriptions can be found here. Mostly the Integer data types in the
# default instructions set of each category end up being a number.
# https://developer.tuya.com/en/docs/iot/standarddescription?id=K9i5ql6waswzq
NUMBERS: dict[str, tuple[NumberEntityDescription, ...]] = {
    # Multi-functional Sensor
    # https://developer.tuya.com/en/docs/iot/categorydgnbj?id=Kaiuz3yorvzg3
    "dgnbj": (
        NumberEntityDescription(
            key=DPCode.ALARM_TIME,
            name="Time",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Smart Kettle
    # https://developer.tuya.com/en/docs/iot/fbh?id=K9gf484m21yq7
    "bh": (
        NumberEntityDescription(
            key=DPCode.TEMP_SET,
            name="Temperature",
            device_class=NumberDeviceClass.TEMPERATURE,
            icon="mdi:thermometer",
            entity_category=EntityCategory.CONFIG,
        ),
        NumberEntityDescription(
            key=DPCode.TEMP_SET_F,
            name="Temperature",
            device_class=NumberDeviceClass.TEMPERATURE,
            icon="mdi:thermometer",
            entity_category=EntityCategory.CONFIG,
        ),
        NumberEntityDescription(
            key=DPCode.TEMP_BOILING_C,
            name="Temperature after boiling",
            device_class=NumberDeviceClass.TEMPERATURE,
            icon="mdi:thermometer",
            entity_category=EntityCategory.CONFIG,
        ),
        NumberEntityDescription(
            key=DPCode.TEMP_BOILING_F,
            name="Temperature after boiling",
            device_class=NumberDeviceClass.TEMPERATURE,
            icon="mdi:thermometer",
            entity_category=EntityCategory.CONFIG,
        ),
        NumberEntityDescription(
            key=DPCode.WARM_TIME,
            name="Heat preservation time",
            icon="mdi:timer",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Smart Pet Feeder
    # https://developer.tuya.com/en/docs/iot/categorycwwsq?id=Kaiuz2b6vydld
    "cwwsq": (
        NumberEntityDescription(
            key=DPCode.MANUAL_FEED,
            name="Feed",
            icon="mdi:bowl",
        ),
        NumberEntityDescription(
            key=DPCode.VOICE_TIMES,
            name="Voice times",
            icon="mdi:microphone",
        ),
    ),
    # Human Presence Sensor
    # https://developer.tuya.com/en/docs/iot/categoryhps?id=Kaiuz42yhn1hs
    "hps": (
        NumberEntityDescription(
            key=DPCode.SENSITIVITY,
            name="Sensitivity",
            entity_category=EntityCategory.CONFIG,
        ),
        NumberEntityDescription(
            key=DPCode.NEAR_DETECTION,
            name="Near detection",
            icon="mdi:signal-distance-variant",
            entity_category=EntityCategory.CONFIG,
        ),
        NumberEntityDescription(
            key=DPCode.FAR_DETECTION,
            name="Far detection",
            icon="mdi:signal-distance-variant",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Coffee maker
    # https://developer.tuya.com/en/docs/iot/categorykfj?id=Kaiuz2p12pc7f
    "kfj": (
        NumberEntityDescription(
            key=DPCode.WATER_SET,
            name="Water level",
            icon="mdi:cup-water",
            entity_category=EntityCategory.CONFIG,
        ),
        NumberEntityDescription(
            key=DPCode.TEMP_SET,
            name="Temperature",
            device_class=NumberDeviceClass.TEMPERATURE,
            icon="mdi:thermometer",
            entity_category=EntityCategory.CONFIG,
        ),
        NumberEntityDescription(
            key=DPCode.WARM_TIME,
            name="Heat preservation time",
            icon="mdi:timer",
            entity_category=EntityCategory.CONFIG,
        ),
        NumberEntityDescription(
            key=DPCode.POWDER_SET,
            name="Powder",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Sous Vide Cooker
    # https://developer.tuya.com/en/docs/iot/categorymzj?id=Kaiuz2vy130ux
    "mzj": (
        NumberEntityDescription(
            key=DPCode.COOK_TEMPERATURE,
            name="Cook temperature",
            icon="mdi:thermometer",
            entity_category=EntityCategory.CONFIG,
        ),
        NumberEntityDescription(
            key=DPCode.COOK_TIME,
            name="Cook time",
            icon="mdi:timer",
            native_unit_of_measurement=TIME_MINUTES,
            entity_category=EntityCategory.CONFIG,
        ),
        NumberEntityDescription(
            key=DPCode.CLOUD_RECIPE_NUMBER,
            name="Cloud recipe",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Robot Vacuum
    # https://developer.tuya.com/en/docs/iot/fsd?id=K9gf487ck1tlo
    "sd": (
        NumberEntityDescription(
            key=DPCode.VOLUME_SET,
            name="Volume",
            icon="mdi:volume-high",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Siren Alarm
    # https://developer.tuya.com/en/docs/iot/categorysgbj?id=Kaiuz37tlpbnu
    "sgbj": (
        NumberEntityDescription(
            key=DPCode.ALARM_TIME,
            name="Time",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Smart Camera
    # https://developer.tuya.com/en/docs/iot/categorysp?id=Kaiuz35leyo12
    "sp": (
        NumberEntityDescription(
            key=DPCode.BASIC_DEVICE_VOLUME,
            name="Volume",
            icon="mdi:volume-high",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Dimmer Switch
    # https://developer.tuya.com/en/docs/iot/categorytgkg?id=Kaiuz0ktx7m0o
    "tgkg": (
        NumberEntityDescription(
            key=DPCode.BRIGHTNESS_MIN_1,
            name="Minimum brightness",
            icon="mdi:lightbulb-outline",
            entity_category=EntityCategory.CONFIG,
        ),
        NumberEntityDescription(
            key=DPCode.BRIGHTNESS_MAX_1,
            name="Maximum brightness",
            icon="mdi:lightbulb-on-outline",
            entity_category=EntityCategory.CONFIG,
        ),
        NumberEntityDescription(
            key=DPCode.BRIGHTNESS_MIN_2,
            name="Minimum brightness 2",
            icon="mdi:lightbulb-outline",
            entity_category=EntityCategory.CONFIG,
        ),
        NumberEntityDescription(
            key=DPCode.BRIGHTNESS_MAX_2,
            name="Maximum brightness 2",
            icon="mdi:lightbulb-on-outline",
            entity_category=EntityCategory.CONFIG,
        ),
        NumberEntityDescription(
            key=DPCode.BRIGHTNESS_MIN_3,
            name="Minimum brightness 3",
            icon="mdi:lightbulb-outline",
            entity_category=EntityCategory.CONFIG,
        ),
        NumberEntityDescription(
            key=DPCode.BRIGHTNESS_MAX_3,
            name="Maximum brightness 3",
            icon="mdi:lightbulb-on-outline",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Dimmer Switch
    # https://developer.tuya.com/en/docs/iot/categorytgkg?id=Kaiuz0ktx7m0o
    "tgq": (
        NumberEntityDescription(
            key=DPCode.BRIGHTNESS_MIN_1,
            name="Minimum brightness",
            icon="mdi:lightbulb-outline",
            entity_category=EntityCategory.CONFIG,
        ),
        NumberEntityDescription(
            key=DPCode.BRIGHTNESS_MAX_1,
            name="Maximum brightness",
            icon="mdi:lightbulb-on-outline",
            entity_category=EntityCategory.CONFIG,
        ),
        NumberEntityDescription(
            key=DPCode.BRIGHTNESS_MIN_2,
            name="Minimum brightness 2",
            icon="mdi:lightbulb-outline",
            entity_category=EntityCategory.CONFIG,
        ),
        NumberEntityDescription(
            key=DPCode.BRIGHTNESS_MAX_2,
            name="Maximum brightness 2",
            icon="mdi:lightbulb-on-outline",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Vibration Sensor
    # https://developer.tuya.com/en/docs/iot/categoryzd?id=Kaiuz3a5vrzno
    "zd": (
        NumberEntityDescription(
            key=DPCode.SENSITIVITY,
            name="Sensitivity",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Fingerbot
    "szjqr": (
        NumberEntityDescription(
            key=DPCode.ARM_DOWN_PERCENT,
            name="Move down %",
            icon="mdi:arrow-down-bold",
            entity_category=EntityCategory.CONFIG,
        ),
        NumberEntityDescription(
            key=DPCode.ARM_UP_PERCENT,
            name="Move up %",
            icon="mdi:arrow-up-bold",
            entity_category=EntityCategory.CONFIG,
        ),
        NumberEntityDescription(
            key=DPCode.CLICK_SUSTAIN_TIME,
            name="Down delay",
            icon="mdi:timer",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Fan
    # https://developer.tuya.com/en/docs/iot/categoryfs?id=Kaiuz1xweel1c
    "fs": (
        NumberEntityDescription(
            key=DPCode.TEMP,
            name="Temperature",
            device_class=NumberDeviceClass.TEMPERATURE,
            icon="mdi:thermometer-lines",
        ),
    ),
    # Humidifier
    # https://developer.tuya.com/en/docs/iot/categoryjsq?id=Kaiuz1smr440b
    "jsq": (
        NumberEntityDescription(
            key=DPCode.TEMP_SET,
            name="Temperature",
            device_class=NumberDeviceClass.TEMPERATURE,
            icon="mdi:thermometer-lines",
        ),
        NumberEntityDescription(
            key=DPCode.TEMP_SET_F,
            name="Temperature",
            device_class=NumberDeviceClass.TEMPERATURE,
            icon="mdi:thermometer-lines",
        ),
    ),
}

# All descriptions can be found here. Mostly the Enum data types in the
# default instructions set of each category end up being a select.
# https://developer.tuya.com/en/docs/iot/standarddescription?id=K9i5ql6waswzq
SELECTS: dict[str, tuple[SelectEntityDescription, ...]] = {
    # Multi-functional Sensor
    # https://developer.tuya.com/en/docs/iot/categorydgnbj?id=Kaiuz3yorvzg3
    "dgnbj": (
        SelectEntityDescription(
            key=DPCode.ALARM_VOLUME,
            name="Volume",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Coffee maker
    # https://developer.tuya.com/en/docs/iot/categorykfj?id=Kaiuz2p12pc7f
    "kfj": (
        SelectEntityDescription(
            key=DPCode.CUP_NUMBER,
            name="Cups",
            icon="mdi:numeric",
        ),
        SelectEntityDescription(
            key=DPCode.CONCENTRATION_SET,
            name="Concentration",
            icon="mdi:altimeter",
            entity_category=EntityCategory.CONFIG,
        ),
        SelectEntityDescription(
            key=DPCode.MATERIAL,
            name="Material",
            entity_category=EntityCategory.CONFIG,
        ),
        SelectEntityDescription(
            key=DPCode.MODE,
            name="Mode",
            icon="mdi:coffee",
        ),
    ),
    # Switch
    # https://developer.tuya.com/en/docs/iot/s?id=K9gf7o5prgf7s
    "kg": (
        SelectEntityDescription(
            key=DPCode.RELAY_STATUS,
            name="Power on behavior",
            device_class=TuyaDeviceClass.RELAY_STATUS,
            entity_category=EntityCategory.CONFIG,
        ),
        SelectEntityDescription(
            key=DPCode.LIGHT_MODE,
            name="Indicator light mode",
            device_class=TuyaDeviceClass.LIGHT_MODE,
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Heater
    # https://developer.tuya.com/en/docs/iot/categoryqn?id=Kaiuz18kih0sm
    "qn": (
        SelectEntityDescription(
            key=DPCode.LEVEL,
            name="Temperature level",
            icon="mdi:thermometer-lines",
        ),
    ),
    # Siren Alarm
    # https://developer.tuya.com/en/docs/iot/categorysgbj?id=Kaiuz37tlpbnu
    "sgbj": (
        SelectEntityDescription(
            key=DPCode.ALARM_VOLUME,
            name="Volume",
            entity_category=EntityCategory.CONFIG,
        ),
        SelectEntityDescription(
            key=DPCode.BRIGHT_STATE,
            name="Brightness",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Smart Camera
    # https://developer.tuya.com/en/docs/iot/categorysp?id=Kaiuz35leyo12
    "sp": (
        SelectEntityDescription(
            key=DPCode.IPC_WORK_MODE,
            name="IPC mode",
            device_class=TuyaDeviceClass.IPC_WORK_MODE,
            entity_category=EntityCategory.CONFIG,
        ),
        SelectEntityDescription(
            key=DPCode.DECIBEL_SENSITIVITY,
            name="Sound detection densitivity",
            icon="mdi:volume-vibrate",
            device_class=TuyaDeviceClass.DECIBEL_SENSITIVITY,
            entity_category=EntityCategory.CONFIG,
        ),
        SelectEntityDescription(
            key=DPCode.RECORD_MODE,
            name="Record mode",
            icon="mdi:record-rec",
            device_class=TuyaDeviceClass.RECORD_MODE,
            entity_category=EntityCategory.CONFIG,
        ),
        SelectEntityDescription(
            key=DPCode.BASIC_NIGHTVISION,
            name="Night vision",
            icon="mdi:theme-light-dark",
            device_class=TuyaDeviceClass.BASIC_NIGHTVISION,
            entity_category=EntityCategory.CONFIG,
        ),
        SelectEntityDescription(
            key=DPCode.BASIC_ANTI_FLICKER,
            name="Anti-flicker",
            icon="mdi:image-outline",
            device_class=TuyaDeviceClass.BASIC_ANTI_FLICKR,
            entity_category=EntityCategory.CONFIG,
        ),
        SelectEntityDescription(
            key=DPCode.MOTION_SENSITIVITY,
            name="Motion detection sensitivity",
            icon="mdi:motion-sensor",
            device_class=TuyaDeviceClass.MOTION_SENSITIVITY,
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # IoT Switch?
    # Note: Undocumented
    "tdq": (
        SelectEntityDescription(
            key=DPCode.RELAY_STATUS,
            name="Power on behavior",
            device_class=TuyaDeviceClass.RELAY_STATUS,
            entity_category=EntityCategory.CONFIG,
        ),
        SelectEntityDescription(
            key=DPCode.LIGHT_MODE,
            name="Indicator light mode",
            device_class=TuyaDeviceClass.LIGHT_MODE,
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Dimmer Switch
    # https://developer.tuya.com/en/docs/iot/categorytgkg?id=Kaiuz0ktx7m0o
    "tgkg": (
        SelectEntityDescription(
            key=DPCode.RELAY_STATUS,
            name="Power on behavior",
            device_class=TuyaDeviceClass.RELAY_STATUS,
            entity_category=EntityCategory.CONFIG,
        ),
        SelectEntityDescription(
            key=DPCode.LIGHT_MODE,
            name="Indicator light mode",
            device_class=TuyaDeviceClass.LIGHT_MODE,
            entity_category=EntityCategory.CONFIG,
        ),
        SelectEntityDescription(
            key=DPCode.LED_TYPE_1,
            name="Light source type",
            device_class=TuyaDeviceClass.LED_TYPE,
            entity_category=EntityCategory.CONFIG,
        ),
        SelectEntityDescription(
            key=DPCode.LED_TYPE_2,
            name="Light 2 source type",
            device_class=TuyaDeviceClass.LED_TYPE,
            entity_category=EntityCategory.CONFIG,
        ),
        SelectEntityDescription(
            key=DPCode.LED_TYPE_3,
            name="Light 3 source type",
            device_class=TuyaDeviceClass.LED_TYPE,
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Dimmer
    # https://developer.tuya.com/en/docs/iot/tgq?id=Kaof8ke9il4k4
    "tgq": (
        SelectEntityDescription(
            key=DPCode.LED_TYPE_1,
            name="Light source type",
            device_class=TuyaDeviceClass.LED_TYPE,
            entity_category=EntityCategory.CONFIG,
        ),
        SelectEntityDescription(
            key=DPCode.LED_TYPE_2,
            name="Light 2 source type",
            device_class=TuyaDeviceClass.LED_TYPE,
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Fingerbot
    "szjqr": (
        SelectEntityDescription(
            key=DPCode.MODE,
            name="Mode",
            device_class=TuyaDeviceClass.FINGERBOT_MODE,
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Robot Vacuum
    # https://developer.tuya.com/en/docs/iot/fsd?id=K9gf487ck1tlo
    "sd": (
        SelectEntityDescription(
            key=DPCode.CISTERN,
            name="Water tank adjustment",
            entity_category=EntityCategory.CONFIG,
            device_class=TuyaDeviceClass.VACUUM_CISTERN,
            icon="mdi:water-opacity",
        ),
        SelectEntityDescription(
            key=DPCode.COLLECTION_MODE,
            name="Dust collection mode",
            entity_category=EntityCategory.CONFIG,
            device_class=TuyaDeviceClass.VACUUM_COLLECTION,
            icon="mdi:air-filter",
        ),
        SelectEntityDescription(
            key=DPCode.MODE,
            name="Mode",
            entity_category=EntityCategory.CONFIG,
            device_class=TuyaDeviceClass.VACUUM_MODE,
            icon="mdi:layers-outline",
        ),
    ),
    # Fan
    # https://developer.tuya.com/en/docs/iot/f?id=K9gf45vs7vkge
    "fs": (
        SelectEntityDescription(
            key=DPCode.FAN_VERTICAL,
            name="Vertical swing flap angle",
            device_class=TuyaDeviceClass.FAN_ANGLE,
            entity_category=EntityCategory.CONFIG,
            icon="mdi:format-vertical-align-center",
        ),
        SelectEntityDescription(
            key=DPCode.FAN_HORIZONTAL,
            name="Horizontal swing flap angle",
            device_class=TuyaDeviceClass.FAN_ANGLE,
            entity_category=EntityCategory.CONFIG,
            icon="mdi:format-horizontal-align-center",
        ),
        SelectEntityDescription(
            key=DPCode.COUNTDOWN,
            name="Countdown",
            device_class=TuyaDeviceClass.COUNTDOWN,
            entity_category=EntityCategory.CONFIG,
            icon="mdi:timer-cog-outline",
        ),
        SelectEntityDescription(
            key=DPCode.COUNTDOWN_SET,
            name="Countdown",
            device_class=TuyaDeviceClass.COUNTDOWN,
            entity_category=EntityCategory.CONFIG,
            icon="mdi:timer-cog-outline",
        ),
    ),
    # Curtain
    # https://developer.tuya.com/en/docs/iot/f?id=K9gf46o5mtfyc
    "cl": (
        SelectEntityDescription(
            key=DPCode.CONTROL_BACK_MODE,
            name="Motor mode",
            device_class=TuyaDeviceClass.CURTAIN_MOTOR_MODE,
            entity_category=EntityCategory.CONFIG,
            icon="mdi:swap-horizontal",
        ),
        SelectEntityDescription(
            key=DPCode.MODE,
            name="Mode",
            device_class=TuyaDeviceClass.CURTAIN_MODE,
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Humidifier
    # https://developer.tuya.com/en/docs/iot/categoryjsq?id=Kaiuz1smr440b
    "jsq": (
        SelectEntityDescription(
            key=DPCode.SPRAY_MODE,
            name="Spray mode",
            device_class=TuyaDeviceClass.HUMIDIFIER_SPRAY_MODE,
            entity_category=EntityCategory.CONFIG,
            icon="mdi:spray",
        ),
        SelectEntityDescription(
            key=DPCode.LEVEL,
            name="Spraying level",
            device_class=TuyaDeviceClass.HUMIDIFIER_LEVEL,
            entity_category=EntityCategory.CONFIG,
            icon="mdi:spray",
        ),
        SelectEntityDescription(
            key=DPCode.MOODLIGHTING,
            name="Moodlighting",
            device_class=TuyaDeviceClass.HUMIDIFIER_MOODLIGHTING,
            entity_category=EntityCategory.CONFIG,
            icon="mdi:lightbulb-multiple",
        ),
        SelectEntityDescription(
            key=DPCode.COUNTDOWN,
            name="Countdown",
            device_class=TuyaDeviceClass.COUNTDOWN,
            entity_category=EntityCategory.CONFIG,
            icon="mdi:timer-cog-outline",
        ),
        SelectEntityDescription(
            key=DPCode.COUNTDOWN_SET,
            name="Countdown",
            device_class=TuyaDeviceClass.COUNTDOWN,
            entity_category=EntityCategory.CONFIG,
            icon="mdi:timer-cog-outline",
        ),
    ),
    # Air Purifier
    # https://developer.tuya.com/en/docs/iot/f?id=K9gf46h2s6dzm
    "kj": (
        SelectEntityDescription(
            key=DPCode.COUNTDOWN,
            name="Countdown",
            device_class=TuyaDeviceClass.COUNTDOWN,
            entity_category=EntityCategory.CONFIG,
            icon="mdi:timer-cog-outline",
        ),
        SelectEntityDescription(
            key=DPCode.COUNTDOWN_SET,
            name="Countdown",
            device_class=TuyaDeviceClass.COUNTDOWN,
            entity_category=EntityCategory.CONFIG,
            icon="mdi:timer-cog-outline",
        ),
    ),
}

# Socket (duplicate of `kg`)
# https://developer.tuya.com/en/docs/iot/s?id=K9gf7o5prgf7s
SELECTS["cz"] = SELECTS["kg"]

# Power Socket (duplicate of `kg`)
# https://developer.tuya.com/en/docs/iot/s?id=K9gf7o5prgf7s
SELECTS["pc"] = SELECTS["kg"]

# Commonly used battery sensors, that are re-used in the sensors down below.
BATTERY_SENSORS: tuple[TuyaSensorEntityDescription, ...] = (
    TuyaSensorEntityDescription(
        key=DPCode.BATTERY_PERCENTAGE,
        name="Battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TuyaSensorEntityDescription(
        key=DPCode.BATTERY_STATE,
        name="Battery state",
        icon="mdi:battery",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TuyaSensorEntityDescription(
        key=DPCode.BATTERY_VALUE,
        name="Battery",
        device_class=SensorDeviceClass.BATTERY,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    TuyaSensorEntityDescription(
        key=DPCode.VA_BATTERY,
        name="Battery",
        device_class=SensorDeviceClass.BATTERY,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)

# All descriptions can be found here. Mostly the Integer data types in the
# default status set of each category (that don't have a set instruction)
# end up being a sensor.
# https://developer.tuya.com/en/docs/iot/standarddescription?id=K9i5ql6waswzq
SENSORS: dict[str, tuple[TuyaSensorEntityDescription, ...]] = {
    # Multi-functional Sensor
    # https://developer.tuya.com/en/docs/iot/categorydgnbj?id=Kaiuz3yorvzg3
    "dgnbj": (
        TuyaSensorEntityDescription(
            key=DPCode.GAS_SENSOR_VALUE,
            name="Gas",
            icon="mdi:gas-cylinder",
            device_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.CH4_SENSOR_VALUE,
            name="Methane",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.VOC_VALUE,
            name="Volatile organic compound",
            device_class=SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.PM25_VALUE,
            name="Particulate matter 2.5 µm",
            device_class=SensorDeviceClass.PM25,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.CO_VALUE,
            name="Carbon monoxide",
            icon="mdi:molecule-co",
            device_class=SensorDeviceClass.CO,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.CO2_VALUE,
            name="Carbon dioxide",
            icon="mdi:molecule-co2",
            device_class=SensorDeviceClass.CO2,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.CH2O_VALUE,
            name="Formaldehyde",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.BRIGHT_STATE,
            name="Luminosity",
            icon="mdi:brightness-6",
        ),
        TuyaSensorEntityDescription(
            key=DPCode.BRIGHT_VALUE,
            name="Luminosity",
            icon="mdi:brightness-6",
            device_class=SensorDeviceClass.ILLUMINANCE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.TEMP_CURRENT,
            name="Temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.HUMIDITY_VALUE,
            name="Humidity",
            device_class=SensorDeviceClass.HUMIDITY,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.SMOKE_SENSOR_VALUE,
            name="Smoke amount",
            icon="mdi:smoke-detector",
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorStateClass.MEASUREMENT,
        ),
        *BATTERY_SENSORS,
    ),
    # Smart Kettle
    # https://developer.tuya.com/en/docs/iot/fbh?id=K9gf484m21yq7
    "bh": (
        TuyaSensorEntityDescription(
            key=DPCode.TEMP_CURRENT,
            name="Current temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.TEMP_CURRENT_F,
            name="Current temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.STATUS,
            name="Status",
            device_class=TuyaDeviceClass.STATUS,
        ),
    ),
    # CO2 Detector
    # https://developer.tuya.com/en/docs/iot/categoryco2bj?id=Kaiuz3wes7yuy
    "co2bj": (
        TuyaSensorEntityDescription(
            key=DPCode.HUMIDITY_VALUE,
            name="Humidity",
            device_class=SensorDeviceClass.HUMIDITY,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.TEMP_CURRENT,
            name="Temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.CO2_VALUE,
            name="Carbon dioxide",
            device_class=SensorDeviceClass.CO2,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        *BATTERY_SENSORS,
    ),
    # Two-way temperature and humidity switch
    # "MOES Temperature and Humidity Smart Switch Module MS-103"
    # Documentation not found
    "wkcz": (
        TuyaSensorEntityDescription(
            key=DPCode.HUMIDITY_VALUE,
            name="Humidity",
            device_class=SensorDeviceClass.HUMIDITY,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.TEMP_CURRENT,
            name="Temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
    ),
    # CO Detector
    # https://developer.tuya.com/en/docs/iot/categorycobj?id=Kaiuz3u1j6q1v
    "cobj": (
        TuyaSensorEntityDescription(
            key=DPCode.CO_VALUE,
            name="Carbon monoxide",
            device_class=SensorDeviceClass.CO,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        *BATTERY_SENSORS,
    ),
    # Smart Pet Feeder
    # https://developer.tuya.com/en/docs/iot/categorycwwsq?id=Kaiuz2b6vydld
    "cwwsq": (
        TuyaSensorEntityDescription(
            key=DPCode.FEED_REPORT,
            name="Last amount",
            icon="mdi:counter",
            state_class=SensorStateClass.MEASUREMENT,
        ),
    ),
    # Air Quality Monitor
    # No specification on Tuya portal
    "hjjcy": (
        TuyaSensorEntityDescription(
            key=DPCode.TEMP_CURRENT,
            name="Temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.HUMIDITY_VALUE,
            name="Humidity",
            device_class=SensorDeviceClass.HUMIDITY,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.CO2_VALUE,
            name="Carbon dioxide",
            device_class=SensorDeviceClass.CO2,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.CH2O_VALUE,
            name="Formaldehyde",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.VOC_VALUE,
            name="Volatile organic compound",
            device_class=SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.PM25_VALUE,
            name="Particulate matter 2.5 µm",
            device_class=SensorDeviceClass.PM25,
            state_class=SensorStateClass.MEASUREMENT,
        ),
    ),
    # Formaldehyde Detector
    # Note: Not documented
    "jqbj": (
        TuyaSensorEntityDescription(
            key=DPCode.CO2_VALUE,
            name="Carbon dioxide",
            device_class=SensorDeviceClass.CO2,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.VOC_VALUE,
            name="Volatile organic compound",
            device_class=SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.PM25_VALUE,
            name="Particulate matter 2.5 µm",
            device_class=SensorDeviceClass.PM25,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.VA_HUMIDITY,
            name="Humidity",
            device_class=SensorDeviceClass.HUMIDITY,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.VA_TEMPERATURE,
            name="Temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.CH2O_VALUE,
            name="Formaldehyde",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        *BATTERY_SENSORS,
    ),
    # Methane Detector
    # https://developer.tuya.com/en/docs/iot/categoryjwbj?id=Kaiuz40u98lkm
    "jwbj": (
        TuyaSensorEntityDescription(
            key=DPCode.CH4_SENSOR_VALUE,
            name="Methane",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        *BATTERY_SENSORS,
    ),
    # Switch
    # https://developer.tuya.com/en/docs/iot/s?id=K9gf7o5prgf7s
    "kg": (
        TuyaSensorEntityDescription(
            key=DPCode.CUR_CURRENT,
            name="Current",
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
            entity_registry_enabled_default=False,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.CUR_POWER,
            name="Power",
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            entity_registry_enabled_default=False,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.CUR_VOLTAGE,
            name="Voltage",
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            entity_registry_enabled_default=False,
        ),
    ),
    # IoT Switch
    # Note: Undocumented
    "tdq": (
        TuyaSensorEntityDescription(
            key=DPCode.CUR_CURRENT,
            name="Current",
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
            entity_registry_enabled_default=False,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.CUR_POWER,
            name="Power",
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            entity_registry_enabled_default=False,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.CUR_VOLTAGE,
            name="Voltage",
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            entity_registry_enabled_default=False,
        ),
    ),
    # Luminance Sensor
    # https://developer.tuya.com/en/docs/iot/categoryldcg?id=Kaiuz3n7u69l8
    "ldcg": (
        TuyaSensorEntityDescription(
            key=DPCode.BRIGHT_STATE,
            name="Luminosity",
            icon="mdi:brightness-6",
        ),
        TuyaSensorEntityDescription(
            key=DPCode.BRIGHT_VALUE,
            name="Luminosity",
            device_class=SensorDeviceClass.ILLUMINANCE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.TEMP_CURRENT,
            name="Temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.HUMIDITY_VALUE,
            name="Humidity",
            device_class=SensorDeviceClass.HUMIDITY,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.CO2_VALUE,
            name="Carbon dioxide",
            device_class=SensorDeviceClass.CO2,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        *BATTERY_SENSORS,
    ),
    # Door and Window Controller
    # https://developer.tuya.com/en/docs/iot/s?id=K9gf48r5zjsy9
    "mc": BATTERY_SENSORS,
    # Door Window Sensor
    # https://developer.tuya.com/en/docs/iot/s?id=K9gf48hm02l8m
    "mcs": BATTERY_SENSORS,
    # Sous Vide Cooker
    # https://developer.tuya.com/en/docs/iot/categorymzj?id=Kaiuz2vy130ux
    "mzj": (
        TuyaSensorEntityDescription(
            key=DPCode.TEMP_CURRENT,
            name="Current temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.STATUS,
            name="Status",
            device_class=TuyaDeviceClass.STATUS,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.REMAIN_TIME,
            name="Remaining time",
            native_unit_of_measurement=TIME_MINUTES,
            icon="mdi:timer",
        ),
    ),
    # PIR Detector
    # https://developer.tuya.com/en/docs/iot/categorypir?id=Kaiuz3ss11b80
    "pir": BATTERY_SENSORS,
    # PM2.5 Sensor
    # https://developer.tuya.com/en/docs/iot/categorypm25?id=Kaiuz3qof3yfu
    "pm2.5": (
        TuyaSensorEntityDescription(
            key=DPCode.PM25_VALUE,
            name="Particulate matter 2.5 µm",
            device_class=SensorDeviceClass.PM25,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.CH2O_VALUE,
            name="Formaldehyde",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.VOC_VALUE,
            name="Volatile organic compound",
            device_class=SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.TEMP_CURRENT,
            name="Temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.CO2_VALUE,
            name="Carbon dioxide",
            device_class=SensorDeviceClass.CO2,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.HUMIDITY_VALUE,
            name="Humidity",
            device_class=SensorDeviceClass.HUMIDITY,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.PM1,
            name="Particulate matter 1.0 µm",
            device_class=SensorDeviceClass.PM1,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.PM10,
            name="Particulate matter 10.0 µm",
            device_class=SensorDeviceClass.PM10,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        *BATTERY_SENSORS,
    ),
    # Heater
    # https://developer.tuya.com/en/docs/iot/categoryqn?id=Kaiuz18kih0sm
    "qn": (
        TuyaSensorEntityDescription(
            key=DPCode.WORK_POWER,
            name="Power",
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
        ),
    ),
    # Gas Detector
    # https://developer.tuya.com/en/docs/iot/categoryrqbj?id=Kaiuz3d162ubw
    "rqbj": (
        TuyaSensorEntityDescription(
            key=DPCode.GAS_SENSOR_VALUE,
            icon="mdi:gas-cylinder",
            device_class=SensorStateClass.MEASUREMENT,
        ),
        *BATTERY_SENSORS,
    ),
    # Water Detector
    # https://developer.tuya.com/en/docs/iot/categorysj?id=Kaiuz3iub2sli
    "sj": BATTERY_SENSORS,
    # Emergency Button
    # https://developer.tuya.com/en/docs/iot/categorysos?id=Kaiuz3oi6agjy
    "sos": BATTERY_SENSORS,
    # Smart Camera
    # https://developer.tuya.com/en/docs/iot/categorysp?id=Kaiuz35leyo12
    "sp": (
        TuyaSensorEntityDescription(
            key=DPCode.SENSOR_TEMPERATURE,
            name="Temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.SENSOR_HUMIDITY,
            name="Humidity",
            device_class=SensorDeviceClass.HUMIDITY,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.WIRELESS_ELECTRICITY,
            name="Battery",
            device_class=SensorDeviceClass.BATTERY,
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
        ),
    ),
    # Fingerbot
    "szjqr": BATTERY_SENSORS,
    # Solar Light
    # https://developer.tuya.com/en/docs/iot/tynd?id=Kaof8j02e1t98
    "tyndj": BATTERY_SENSORS,
    # Volatile Organic Compound Sensor
    # Note: Undocumented in cloud API docs, based on test device
    "voc": (
        TuyaSensorEntityDescription(
            key=DPCode.CO2_VALUE,
            name="Carbon dioxide",
            device_class=SensorDeviceClass.CO2,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.PM25_VALUE,
            name="Particulate matter 2.5 µm",
            device_class=SensorDeviceClass.PM25,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.CH2O_VALUE,
            name="Formaldehyde",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.HUMIDITY_VALUE,
            name="Humidity",
            device_class=SensorDeviceClass.HUMIDITY,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.TEMP_CURRENT,
            name="Temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.VOC_VALUE,
            name="Volatile organic compound",
            device_class=SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        *BATTERY_SENSORS,
    ),
    # Thermostatic Radiator Valve
    # Not documented
    "wkf": BATTERY_SENSORS,
    # Temperature and Humidity Sensor
    # https://developer.tuya.com/en/docs/iot/categorywsdcg?id=Kaiuz3hinij34
    "wsdcg": (
        TuyaSensorEntityDescription(
            key=DPCode.VA_TEMPERATURE,
            name="Temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.TEMP_CURRENT,
            name="Temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.VA_HUMIDITY,
            name="Humidity",
            device_class=SensorDeviceClass.HUMIDITY,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.HUMIDITY_VALUE,
            name="Humidity",
            device_class=SensorDeviceClass.HUMIDITY,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.BRIGHT_VALUE,
            name="Luminosity",
            device_class=SensorDeviceClass.ILLUMINANCE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        *BATTERY_SENSORS,
    ),
    # Pressure Sensor
    # https://developer.tuya.com/en/docs/iot/categoryylcg?id=Kaiuz3kc2e4gm
    "ylcg": (
        TuyaSensorEntityDescription(
            key=DPCode.PRESSURE_VALUE,
            device_class=SensorDeviceClass.PRESSURE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        *BATTERY_SENSORS,
    ),
    # Smoke Detector
    # https://developer.tuya.com/en/docs/iot/categoryywbj?id=Kaiuz3f6sf952
    "ywbj": (
        TuyaSensorEntityDescription(
            key=DPCode.SMOKE_SENSOR_VALUE,
            name="Smoke amount",
            icon="mdi:smoke-detector",
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorStateClass.MEASUREMENT,
        ),
        *BATTERY_SENSORS,
    ),
    # Vibration Sensor
    # https://developer.tuya.com/en/docs/iot/categoryzd?id=Kaiuz3a5vrzno
    "zd": BATTERY_SENSORS,
    # Smart Electricity Meter
    # https://developer.tuya.com/en/docs/iot/smart-meter?id=Kaiuz4gv6ack7
    "zndb": (
        TuyaSensorEntityDescription(
            key=DPCode.FORWARD_ENERGY_TOTAL,
            name="Total energy",
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.PHASE_A,
            name="Phase A current",
            device_class=SensorDeviceClass.CURRENT,
            native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
            state_class=SensorStateClass.MEASUREMENT,
            subkey="electriccurrent",
        ),
        TuyaSensorEntityDescription(
            key=DPCode.PHASE_A,
            name="Phase A power",
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=POWER_KILO_WATT,
            subkey="power",
        ),
        TuyaSensorEntityDescription(
            key=DPCode.PHASE_A,
            name="Phase A voltage",
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
            subkey="voltage",
        ),
        TuyaSensorEntityDescription(
            key=DPCode.PHASE_B,
            name="Phase B current",
            device_class=SensorDeviceClass.CURRENT,
            native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
            state_class=SensorStateClass.MEASUREMENT,
            subkey="electriccurrent",
        ),
        TuyaSensorEntityDescription(
            key=DPCode.PHASE_B,
            name="Phase B power",
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=POWER_KILO_WATT,
            subkey="power",
        ),
        TuyaSensorEntityDescription(
            key=DPCode.PHASE_B,
            name="Phase B voltage",
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
            subkey="voltage",
        ),
        TuyaSensorEntityDescription(
            key=DPCode.PHASE_C,
            name="Phase C current",
            device_class=SensorDeviceClass.CURRENT,
            native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
            state_class=SensorStateClass.MEASUREMENT,
            subkey="electriccurrent",
        ),
        TuyaSensorEntityDescription(
            key=DPCode.PHASE_C,
            name="Phase C power",
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=POWER_KILO_WATT,
            subkey="power",
        ),
        TuyaSensorEntityDescription(
            key=DPCode.PHASE_C,
            name="Phase C voltage",
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
            subkey="voltage",
        ),
    ),
    # Circuit Breaker
    # https://developer.tuya.com/en/docs/iot/dlq?id=Kb0kidk9enyh8
    "dlq": (
        TuyaSensorEntityDescription(
            key=DPCode.TOTAL_FORWARD_ENERGY,
            name="Total energy",
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.PHASE_A,
            name="Phase A current",
            device_class=SensorDeviceClass.CURRENT,
            native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
            state_class=SensorStateClass.MEASUREMENT,
            subkey="electriccurrent",
        ),
        TuyaSensorEntityDescription(
            key=DPCode.PHASE_A,
            name="Phase A power",
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=POWER_KILO_WATT,
            subkey="power",
        ),
        TuyaSensorEntityDescription(
            key=DPCode.PHASE_A,
            name="Phase A voltage",
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
            subkey="voltage",
        ),
        TuyaSensorEntityDescription(
            key=DPCode.PHASE_B,
            name="Phase B current",
            device_class=SensorDeviceClass.CURRENT,
            native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
            state_class=SensorStateClass.MEASUREMENT,
            subkey="electriccurrent",
        ),
        TuyaSensorEntityDescription(
            key=DPCode.PHASE_B,
            name="Phase B power",
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=POWER_KILO_WATT,
            subkey="power",
        ),
        TuyaSensorEntityDescription(
            key=DPCode.PHASE_B,
            name="Phase B voltage",
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
            subkey="voltage",
        ),
        TuyaSensorEntityDescription(
            key=DPCode.PHASE_C,
            name="Phase C current",
            device_class=SensorDeviceClass.CURRENT,
            native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
            state_class=SensorStateClass.MEASUREMENT,
            subkey="electriccurrent",
        ),
        TuyaSensorEntityDescription(
            key=DPCode.PHASE_C,
            name="Phase C power",
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=POWER_KILO_WATT,
            subkey="power",
        ),
        TuyaSensorEntityDescription(
            key=DPCode.PHASE_C,
            name="Phase C voltage",
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
            subkey="voltage",
        ),
    ),
    # Robot Vacuum
    # https://developer.tuya.com/en/docs/iot/fsd?id=K9gf487ck1tlo
    "sd": (
        TuyaSensorEntityDescription(
            key=DPCode.CLEAN_AREA,
            name="Cleaning area",
            icon="mdi:texture-box",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.CLEAN_TIME,
            name="Cleaning time",
            icon="mdi:progress-clock",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.TOTAL_CLEAN_AREA,
            name="Total Cleaning Area",
            icon="mdi:texture-box",
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.TOTAL_CLEAN_TIME,
            name="Total cleaning time",
            icon="mdi:history",
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.TOTAL_CLEAN_COUNT,
            name="Total cleaning times",
            icon="mdi:counter",
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.DUSTER_CLOTH,
            name="Duster cloth life",
            icon="mdi:ticket-percent-outline",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.EDGE_BRUSH,
            name="Side brush life",
            icon="mdi:ticket-percent-outline",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.FILTER_LIFE,
            name="Filter life",
            icon="mdi:ticket-percent-outline",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.ROLL_BRUSH,
            name="Rolling brush life",
            icon="mdi:ticket-percent-outline",
            state_class=SensorStateClass.MEASUREMENT,
        ),
    ),
    # Curtain
    # https://developer.tuya.com/en/docs/iot/s?id=K9gf48qy7wkre
    "cl": (
        TuyaSensorEntityDescription(
            key=DPCode.TIME_TOTAL,
            name="Last operation duration",
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:progress-clock",
        ),
    ),
    # Humidifier
    # https://developer.tuya.com/en/docs/iot/s?id=K9gf48qwjz0i3
    "jsq": (
        TuyaSensorEntityDescription(
            key=DPCode.HUMIDITY_CURRENT,
            name="Humidity",
            device_class=SensorDeviceClass.HUMIDITY,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.TEMP_CURRENT,
            name="Temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.TEMP_CURRENT_F,
            name="Temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.LEVEL_CURRENT,
            name="Water level",
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:waves-arrow-up",
        ),
    ),
    # Air Purifier
    # https://developer.tuya.com/en/docs/iot/s?id=K9gf48r41mn81
    "kj": (
        TuyaSensorEntityDescription(
            key=DPCode.FILTER,
            name="Filter utilization",
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:ticket-percent-outline",
        ),
        TuyaSensorEntityDescription(
            key=DPCode.PM25,
            name="Particulate matter 2.5 µm",
            device_class=SensorDeviceClass.PM25,
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:molecule",
        ),
        TuyaSensorEntityDescription(
            key=DPCode.TEMP,
            name="Temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.HUMIDITY,
            name="Humidity",
            device_class=SensorDeviceClass.HUMIDITY,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.TVOC,
            name="Total volatile organic compound",
            device_class=SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.ECO2,
            name="Concentration of carbon dioxide",
            device_class=SensorDeviceClass.CO2,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.TOTAL_TIME,
            name="Total operating time",
            icon="mdi:history",
            state_class=SensorStateClass.TOTAL_INCREASING,
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.TOTAL_PM,
            name="Total absorption of particles",
            icon="mdi:texture-box",
            state_class=SensorStateClass.TOTAL_INCREASING,
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        TuyaSensorEntityDescription(
            key=DPCode.AIR_QUALITY,
            name="Air quality",
            icon="mdi:air-filter",
            device_class=TuyaDeviceClass.AIR_QUALITY,
        ),
    ),
    # Fan
    # https://developer.tuya.com/en/docs/iot/s?id=K9gf48quojr54
    "fs": (
        TuyaSensorEntityDescription(
            key=DPCode.TEMP_CURRENT,
            name="Temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
    ),
}

# Socket (duplicate of `kg`)
# https://developer.tuya.com/en/docs/iot/s?id=K9gf7o5prgf7s
SENSORS["cz"] = SENSORS["kg"]

# Power Socket (duplicate of `kg`)
# https://developer.tuya.com/en/docs/iot/s?id=K9gf7o5prgf7s
SENSORS["pc"] = SENSORS["kg"]


# All descriptions can be found here:
# https://developer.tuya.com/en/docs/iot/standarddescription?id=K9i5ql6waswzq
SIRENS: dict[str, tuple[SirenEntityDescription, ...]] = {
    # Multi-functional Sensor
    # https://developer.tuya.com/en/docs/iot/categorydgnbj?id=Kaiuz3yorvzg3
    "dgnbj": (
        SirenEntityDescription(
            key=DPCode.ALARM_SWITCH,
            name="Siren",
        ),
    ),
    # Siren Alarm
    # https://developer.tuya.com/en/docs/iot/categorysgbj?id=Kaiuz37tlpbnu
    "sgbj": (
        SirenEntityDescription(
            key=DPCode.ALARM_SWITCH,
            name="Siren",
        ),
    ),
    # Smart Camera
    # https://developer.tuya.com/en/docs/iot/categorysp?id=Kaiuz35leyo12
    "sp": (
        SirenEntityDescription(
            key=DPCode.SIREN_SWITCH,
            name="Siren",
        ),
    ),
}


# All descriptions can be found here. Mostly the Boolean data types in the
# default instruction set of each category end up being a Switch.
# https://developer.tuya.com/en/docs/iot/standarddescription?id=K9i5ql6waswzq
SWITCHES: dict[str, tuple[SwitchEntityDescription, ...]] = {
    # Smart Kettle
    # https://developer.tuya.com/en/docs/iot/fbh?id=K9gf484m21yq7
    "bh": (
        SwitchEntityDescription(
            key=DPCode.START,
            name="Start",
            icon="mdi:kettle-steam",
        ),
        SwitchEntityDescription(
            key=DPCode.WARM,
            name="Heat Preservation",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Smart Pet Feeder
    # https://developer.tuya.com/en/docs/iot/categorycwwsq?id=Kaiuz2b6vydld
    "cwwsq": (
        SwitchEntityDescription(
            key=DPCode.SLOW_FEED,
            name="Slow Feed",
            icon="mdi:speedometer-slow",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Pet Water Feeder
    # https://developer.tuya.com/en/docs/iot/f?id=K9gf46aewxem5
    "cwysj": (
        SwitchEntityDescription(
            key=DPCode.FILTER_RESET,
            name="Filter reset",
            icon="mdi:filter",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.PUMP_RESET,
            name="Water pump reset",
            icon="mdi:pump",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH,
            name="Power",
        ),
        SwitchEntityDescription(
            key=DPCode.WATER_RESET,
            name="Reset of water usage days",
            icon="mdi:water-sync",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.UV,
            name="UV Sterilization",
            icon="mdi:lightbulb",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Light
    # https://developer.tuya.com/en/docs/iot/f?id=K9i5ql3v98hn3
    "dj": (
        # There are sockets available with an RGB light
        # that advertise as `dj`, but provide an additional
        # switch to control the plug.
        SwitchEntityDescription(
            key=DPCode.SWITCH,
            name="Plug",
        ),
    ),
    # Cirquit Breaker
    "dlq": (
        SwitchEntityDescription(
            key=DPCode.CHILD_LOCK,
            name="Child Lock",
            icon="mdi:account-lock",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH,
            name="Switch",
        ),
    ),
    # Wake Up Light II
    # Not documented
    "hxd": (
        SwitchEntityDescription(
            key=DPCode.SWITCH_1,
            name="Radio",
            icon="mdi:radio",
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_2,
            name="Alarm 1",
            icon="mdi:alarm",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_3,
            name="Alarm 2",
            icon="mdi:alarm",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_4,
            name="Alarm 3",
            icon="mdi:alarm",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_5,
            name="Alarm 4",
            icon="mdi:alarm",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_6,
            name="Sleep Aid",
            icon="mdi:power-sleep",
        ),
    ),
    # Two-way temperature and humidity switch
    # "MOES Temperature and Humidity Smart Switch Module MS-103"
    # Documentation not found
    "wkcz": (
        SwitchEntityDescription(
            key=DPCode.SWITCH_1,
            name="Switch 1",
            device_class=SwitchDeviceClass.OUTLET,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_2,
            name="Switch 2",
            device_class=SwitchDeviceClass.OUTLET,
        ),
    ),
    # Switch
    # https://developer.tuya.com/en/docs/iot/s?id=K9gf7o5prgf7s
    "kg": (
        SwitchEntityDescription(
            key=DPCode.CHILD_LOCK,
            name="Child Lock",
            icon="mdi:account-lock",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_1,
            name="Switch 1",
            device_class=SwitchDeviceClass.OUTLET,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_2,
            name="Switch 2",
            device_class=SwitchDeviceClass.OUTLET,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_3,
            name="Switch 3",
            device_class=SwitchDeviceClass.OUTLET,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_4,
            name="Switch 4",
            device_class=SwitchDeviceClass.OUTLET,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_5,
            name="Switch 5",
            device_class=SwitchDeviceClass.OUTLET,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_6,
            name="Switch 6",
            device_class=SwitchDeviceClass.OUTLET,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_7,
            name="Switch 7",
            device_class=SwitchDeviceClass.OUTLET,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_8,
            name="Switch 8",
            device_class=SwitchDeviceClass.OUTLET,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_USB1,
            name="USB 1",
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_USB2,
            name="USB 2",
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_USB3,
            name="USB 3",
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_USB4,
            name="USB 4",
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_USB5,
            name="USB 5",
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_USB6,
            name="USB 6",
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH,
            name="Switch",
            device_class=SwitchDeviceClass.OUTLET,
        ),
    ),
    # Air Purifier
    # https://developer.tuya.com/en/docs/iot/f?id=K9gf46h2s6dzm
    "kj": (
        SwitchEntityDescription(
            key=DPCode.ANION,
            name="Ionizer",
            icon="mdi:minus-circle-outline",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.FILTER_RESET,
            name="Filter cartridge reset",
            icon="mdi:filter",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.LOCK,
            name="Child lock",
            icon="mdi:account-lock",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH,
            name="Power",
        ),
        SwitchEntityDescription(
            key=DPCode.WET,
            name="Humidification",
            icon="mdi:water-percent",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.UV,
            name="UV Sterilization",
            icon="mdi:minus-circle-outline",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Air conditioner
    # https://developer.tuya.com/en/docs/iot/categorykt?id=Kaiuz0z71ov2n
    "kt": (
        SwitchEntityDescription(
            key=DPCode.ANION,
            name="Ionizer",
            icon="mdi:minus-circle-outline",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.LOCK,
            name="Child Lock",
            icon="mdi:account-lock",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Sous Vide Cooker
    # https://developer.tuya.com/en/docs/iot/categorymzj?id=Kaiuz2vy130ux
    "mzj": (
        SwitchEntityDescription(
            key=DPCode.SWITCH,
            name="Switch",
            icon="mdi:pot-steam",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Power Socket
    # https://developer.tuya.com/en/docs/iot/s?id=K9gf7o5prgf7s
    "pc": (
        SwitchEntityDescription(
            key=DPCode.CHILD_LOCK,
            name="Child Lock",
            icon="mdi:account-lock",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_1,
            name="Socket 1",
            device_class=SwitchDeviceClass.OUTLET,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_2,
            name="Socket 2",
            device_class=SwitchDeviceClass.OUTLET,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_3,
            name="Socket 3",
            device_class=SwitchDeviceClass.OUTLET,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_4,
            name="Socket 4",
            device_class=SwitchDeviceClass.OUTLET,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_5,
            name="Socket 5",
            device_class=SwitchDeviceClass.OUTLET,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_6,
            name="Socket 6",
            device_class=SwitchDeviceClass.OUTLET,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_USB1,
            name="USB 1",
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_USB2,
            name="USB 2",
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_USB3,
            name="USB 3",
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_USB4,
            name="USB 4",
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_USB5,
            name="USB 5",
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_USB6,
            name="USB 6",
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH,
            name="Socket",
            device_class=SwitchDeviceClass.OUTLET,
        ),
    ),
    # Unknown product with switch capabilities
    # Fond in some diffusers, plugs and PIR flood lights
    # Not documented
    "qjdcz": (
        SwitchEntityDescription(
            key=DPCode.SWITCH_1,
            name="Switch",
        ),
    ),
    # Heater
    # https://developer.tuya.com/en/docs/iot/categoryqn?id=Kaiuz18kih0sm
    "qn": (
        SwitchEntityDescription(
            key=DPCode.ANION,
            name="Ionizer",
            icon="mdi:minus-circle-outline",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.LOCK,
            name="Child Lock",
            icon="mdi:account-lock",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Robot Vacuum
    # https://developer.tuya.com/en/docs/iot/fsd?id=K9gf487ck1tlo
    "sd": (
        SwitchEntityDescription(
            key=DPCode.SWITCH_DISTURB,
            name="Do Not Disturb",
            icon="mdi:minus-circle",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.VOICE_SWITCH,
            name="Mute Voice",
            icon="mdi:account-voice",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Siren Alarm
    # https://developer.tuya.com/en/docs/iot/categorysgbj?id=Kaiuz37tlpbnu
    "sgbj": (
        SwitchEntityDescription(
            key=DPCode.MUFFLING,
            name="Mute",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Smart Camera
    # https://developer.tuya.com/en/docs/iot/categorysp?id=Kaiuz35leyo12
    "sp": (
        SwitchEntityDescription(
            key=DPCode.WIRELESS_BATTERYLOCK,
            name="Battery Lock",
            icon="mdi:battery-lock",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.CRY_DETECTION_SWITCH,
            icon="mdi:emoticon-cry",
            name="Cry Detection",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.DECIBEL_SWITCH,
            icon="mdi:microphone-outline",
            name="Sound Detection",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.RECORD_SWITCH,
            icon="mdi:record-rec",
            name="Video Recording",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.MOTION_RECORD,
            icon="mdi:record-rec",
            name="Motion Recording",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.BASIC_PRIVATE,
            icon="mdi:eye-off",
            name="Privacy Mode",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.BASIC_FLIP,
            icon="mdi:flip-horizontal",
            name="Flip",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.BASIC_OSD,
            icon="mdi:watermark",
            name="Time Watermark",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.BASIC_WDR,
            icon="mdi:watermark",
            name="Wide Dynamic Range",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.MOTION_TRACKING,
            icon="mdi:motion-sensor",
            name="Motion Tracking",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.MOTION_SWITCH,
            icon="mdi:motion-sensor",
            name="Motion Alarm",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Fingerbot
    "szjqr": (
        SwitchEntityDescription(
            key=DPCode.SWITCH,
            name="Switch",
            icon="mdi:cursor-pointer",
        ),
    ),
    # IoT Switch?
    # Note: Undocumented
    "tdq": (
        SwitchEntityDescription(
            key=DPCode.SWITCH_1,
            name="Switch 1",
            device_class=SwitchDeviceClass.OUTLET,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_2,
            name="Switch 2",
            device_class=SwitchDeviceClass.OUTLET,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_3,
            name="Switch 3",
            device_class=SwitchDeviceClass.OUTLET,
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_4,
            name="Switch 4",
            device_class=SwitchDeviceClass.OUTLET,
        ),
        SwitchEntityDescription(
            key=DPCode.CHILD_LOCK,
            name="Child Lock",
            icon="mdi:account-lock",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Solar Light
    # https://developer.tuya.com/en/docs/iot/tynd?id=Kaof8j02e1t98
    "tyndj": (
        SwitchEntityDescription(
            key=DPCode.SWITCH_SAVE_ENERGY,
            name="Energy Saving",
            icon="mdi:leaf",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Thermostatic Radiator Valve
    # Not documented
    "wkf": (
        SwitchEntityDescription(
            key=DPCode.CHILD_LOCK,
            name="Child Lock",
            icon="mdi:account-lock",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.WINDOW_CHECK,
            name="Open Window Detection",
            icon="mdi:window-open",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Ceiling Light
    # https://developer.tuya.com/en/docs/iot/ceiling-light?id=Kaiuz03xxfc4r
    "xdd": (
        SwitchEntityDescription(
            key=DPCode.DO_NOT_DISTURB,
            name="Do not disturb",
            icon="mdi:minus-circle-outline",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Diffuser
    # https://developer.tuya.com/en/docs/iot/categoryxxj?id=Kaiuz1f9mo6bl
    "xxj": (
        SwitchEntityDescription(
            key=DPCode.SWITCH,
            name="Power",
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_SPRAY,
            name="Spray",
            icon="mdi:spray",
        ),
        SwitchEntityDescription(
            key=DPCode.SWITCH_VOICE,
            name="Voice",
            icon="mdi:account-voice",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Smart Electricity Meter
    # https://developer.tuya.com/en/docs/iot/smart-meter?id=Kaiuz4gv6ack7
    "zndb": (
        SwitchEntityDescription(
            key=DPCode.SWITCH,
            name="Switch",
        ),
    ),
    # Fan
    # https://developer.tuya.com/en/docs/iot/categoryfs?id=Kaiuz1xweel1c
    "fs": (
        SwitchEntityDescription(
            key=DPCode.ANION,
            name="Anion",
            icon="mdi:atom",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.HUMIDIFIER,
            name="Humidification",
            icon="mdi:air-humidifier",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.OXYGEN,
            name="Oxygen Bar",
            icon="mdi:molecule",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.FAN_COOL,
            name="Natural Wind",
            icon="mdi:weather-windy",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.FAN_BEEP,
            name="Sound",
            icon="mdi:minus-circle",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.CHILD_LOCK,
            name="Child Lock",
            icon="mdi:account-lock",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Curtain
    # https://developer.tuya.com/en/docs/iot/f?id=K9gf46o5mtfyc
    "cl": (
        SwitchEntityDescription(
            key=DPCode.CONTROL_BACK,
            name="Reverse",
            icon="mdi:swap-horizontal",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.OPPOSITE,
            name="Reverse",
            icon="mdi:swap-horizontal",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
    # Humidifier
    # https://developer.tuya.com/en/docs/iot/categoryjsq?id=Kaiuz1smr440b
    "jsq": (
        SwitchEntityDescription(
            key=DPCode.SWITCH_SOUND,
            name="Voice",
            icon="mdi:account-voice",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.SLEEP,
            name="Sleep",
            icon="mdi:power-sleep",
            entity_category=EntityCategory.CONFIG,
        ),
        SwitchEntityDescription(
            key=DPCode.STERILIZATION,
            name="Sterilization",
            icon="mdi:minus-circle-outline",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
}

# Socket (duplicate of `pc`)
# https://developer.tuya.com/en/docs/iot/s?id=K9gf7o5prgf7s
SWITCHES["cz"] = SWITCHES["pc"]


VACUUMS: tuple[str, ...] = (
    "sd",
)
