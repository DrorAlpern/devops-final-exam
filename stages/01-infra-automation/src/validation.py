"""Validation rules for simulated machine definitions."""
import re
from jsonschema import Draft202012Validator

MACHINE_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string", "minLength": 1, "maxLength": 63,
            "pattern": r"^[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?$",
        },
        "os": {"type": "string", "enum": ["Ubuntu", "CentOS"]},
        "cpu": {"type": "integer", "minimum": 1},
        "ram": {"type": "integer", "minimum": 1},
    },
    "required": ["name", "os", "cpu", "ram"],
    "additionalProperties": False,
}
FIELD_MESSAGES = {
    "name": "Use 1-63 letters, digits or hyphens; start and end with a letter or digit.",
    "os": "Choose Ubuntu or CentOS.",
    "cpu": "CPU must be a positive whole number, such as 2 or 2vCPU.",
    "ram": "RAM must be a positive whole number in GB, such as 4 or 4GB.",
}
_VALIDATOR = Draft202012Validator(MACHINE_SCHEMA)


def validate_field(field, value):
    if not Draft202012Validator(MACHINE_SCHEMA["properties"][field]).is_valid(value):
        raise ValueError(FIELD_MESSAGES[field])


def validate_machine(data):
    errors = list(_VALIDATOR.iter_errors(data))
    if errors:
        field = next(iter(errors[0].path), None)
        raise ValueError(FIELD_MESSAGES.get(field, "Machine fields must be name, os, cpu and ram."))


def parse_resource(raw, field):
    unit = "vcpu" if field == "cpu" else "gb"
    match = re.fullmatch(r"([0-9]+)\s*(?:" + unit + r")?", raw.strip(), re.IGNORECASE)
    if not match:
        raise ValueError(FIELD_MESSAGES[field])
    value = int(match.group(1))
    validate_field(field, value)
    return value
