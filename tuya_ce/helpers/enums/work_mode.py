from homeassistant.backports.enum import StrEnum


class WorkMode(StrEnum):
    """Work modes."""

    COLOUR = "colour"
    MUSIC = "music"
    SCENE = "scene"
    WHITE = "white"
