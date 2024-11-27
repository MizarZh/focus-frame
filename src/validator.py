from jsonschema import validate

schema = {
    "type": "object",
    "properties": {
        "presets_name": {"type": "string"},
        "presets": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "preset_name": {"type": "string"},
                    "alpha": {"type": "number"},
                    "xy_abs": {"type": "boolean"},
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "wh_abs": {"type": "boolean"},
                    "w": {"type": "number"},
                    "h": {"type": "number"},
                    "color": {"type": "string"},
                },
            },
        },
    },
}


def preset_validator(preset):
    try:
        validate(instance=preset, schema=schema)
        return True
    except Exception:
        return False
