from homeassistant.backports.enum import StrEnum
from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_DISARMED,
    STATE_ALARM_TRIGGERED,
)


class Mode(StrEnum):
    """Alarm modes."""

    ARM = "arm"
    DISARMED = "disarmed"
    HOME = "home"
    SOS = "sos"


STATE_MAPPING: dict[str, str] = {
    Mode.DISARMED: STATE_ALARM_DISARMED,
    Mode.ARM: STATE_ALARM_ARMED_AWAY,
    Mode.HOME: STATE_ALARM_ARMED_HOME,
    Mode.SOS: STATE_ALARM_TRIGGERED,
}
