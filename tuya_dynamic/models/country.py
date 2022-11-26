from dataclasses import dataclass

from tuya_iot import TuyaCloudOpenAPIEndpoint


@dataclass
class Country:
    """Describe a supported country."""
    name: str
    country_code: str
    endpoint: str = TuyaCloudOpenAPIEndpoint.AMERICA
