from jsonschema import Draft7Validator
from jsonschema.exceptions import best_match

_schema = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "http://example.com/example.json",
    "type": "object",
    "default": {},
    "additionalProperties": False,
    "required": [
    ],
    "properties": {
        "sub": {
            "$id": "#/properties/sub",
            "type": "array",
            "default": [],
            "examples": [
                [
                    "suisei",
                    "mea"
                ]
            ],
            "additionalItems": True,
            "items": {
                "$id": "#/properties/sub/items",
                "type": "string",
                "default": "",
                "examples": [
                    "suisei",
                    "mea"
                ]
            }
        },
        "notif": {
            "$id": "#/properties/notif",
            "type": "array",
            "default": [],
            "examples": [
                [
                    "bili_plain_dyn",
                    "bili_img_dyn",
                    "ytb_live"
                ]
            ],
            "additionalItems": False,
            "items": {
                "$id": "#/properties/notif/items",
                "type": "string",
                "default": "",
                "examples": [
                    "bili_plain_dyn",
                    "bili_rt_dyn",
                    "bili_img_dyn",
                    "bili_video",
                    "t_tweet",
                    "t_rt",
                    "ytb_live",
                    "ytb_sched",
                    "ytb_reminder",
                    "ytb_video"
                ]
            }
        }
    }
}

default_dict = {
    "sub": [],
    "notif": []
}

_validator = Draft7Validator(_schema)


def validate(obj):
    errors = best_match(_validator.iter_errors(obj))
    if errors:
        return False, str(errors)
    return True, None
