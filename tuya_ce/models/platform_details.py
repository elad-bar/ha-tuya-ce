from homeassistant.helpers.entity import EntityDescription


class PlatformDetails:
    enabled: bool
    simple: bool
    entity_description: EntityDescription | None

    def __init__(self, enabled: bool, simple: bool, entity_description: EntityDescription | None):
        self.enabled = enabled
        self.simple = simple
        self.entity_description = entity_description
