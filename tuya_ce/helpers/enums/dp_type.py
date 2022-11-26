from homeassistant.backports.enum import StrEnum


class DPType(StrEnum):
    """Data point types."""

    BOOLEAN = "Boolean"
    ENUM = "Enum"
    INTEGER = "Integer"
    JSON = "Json"
    RAW = "Raw"
    STRING = "String"
