from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN

from .enums.dp_code import DPCode

"""
Old lights where in `tuya.{device_id}` format, now the DPCode is added.

If the device is a previously supported light category and still has
the old format for the unique ID, migrate it to the new format.

Previously only devices providing the SWITCH_LED DPCode were supported,
thus this can be added to those existing IDs.

`tuya.{device_id}` -> `tuya.{device_id}{SWITCH_LED}`

Old switches has different formats for the unique ID, but is mappable.

If the device is a previously supported switch category and still has
the old format for the unique ID, migrate it to the new format.

`tuya.{device_id}` -> `tuya.{device_id}{SWITCH}`
`tuya.{device_id}_1` -> `tuya.{device_id}{SWITCH_1}`

In all other cases, the unique ID is not changed.
"""

TUYA_LEGACY_MAPPING = {
    LIGHT_DOMAIN: {
        "": DPCode.SWITCH_LED
    },
    SWITCH_DOMAIN: {
        "": DPCode.SWITCH,
        "_1": DPCode.SWITCH_1,
        "_2": DPCode.SWITCH_2,
        "_3": DPCode.SWITCH_3,
        "_4": DPCode.SWITCH_4,
        "_5": DPCode.SWITCH_5,
        "_6": DPCode.SWITCH_6,
        "_usb1": DPCode.SWITCH_USB1,
        "_usb2": DPCode.SWITCH_USB2,
        "_usb3": DPCode.SWITCH_USB3,
        "_usb4": DPCode.SWITCH_USB4,
        "_usb5": DPCode.SWITCH_USB5,
        "_usb6": DPCode.SWITCH_USB6
    }
}


TUYA_LEGACY_CATEGORIES = {
    "dc": LIGHT_DOMAIN,
    "dd": LIGHT_DOMAIN,
    "dj": LIGHT_DOMAIN,
    "fs": LIGHT_DOMAIN,
    "fwl": LIGHT_DOMAIN,
    "jsq": LIGHT_DOMAIN,
    "xdd": LIGHT_DOMAIN,
    # "xxj": LIGHT_DOMAIN,
    "bh": SWITCH_DOMAIN,
    "cwysj": SWITCH_DOMAIN,
    "cz": SWITCH_DOMAIN,
    "dlq": SWITCH_DOMAIN,
    "kg": SWITCH_DOMAIN,
    "kj": SWITCH_DOMAIN,
    "pc": SWITCH_DOMAIN,
    "xxj": SWITCH_DOMAIN
}
