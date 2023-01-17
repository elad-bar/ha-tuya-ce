import dataclasses
import json


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)

        elif isinstance(obj, set):
            return list(obj)

        return super().default(obj)
