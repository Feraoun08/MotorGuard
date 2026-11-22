

import re


ROOT_TOPIC = "motorguard"

TOPIC_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")


def validate_topic_component(value: str, field_name: str) -> str:


    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")

    value = value.strip()

    if not value:
        raise ValueError(f"{field_name} cannot be empty")

    if not TOPIC_PATTERN.fullmatch(value):
        raise ValueError(
            f"Invalid {field_name}: {value!r}. "
            "Only letters, numbers, hyphens and underscores are allowed."
        )

    return value


def telemetry_topic(
    factory_id: str,
    motor_id: str,
) -> str:
    """
    motorguard/factories/FACTORY_001/motors/MOTOR_001/telemetry
    """

    factory_id = validate_topic_component(
        factory_id,
        "factory_id",
    )

    motor_id = validate_topic_component(
        motor_id,
        "motor_id",
    )

    return (
        f"{ROOT_TOPIC}/factories/{factory_id}"
        f"/motors/{motor_id}/telemetry"
    )


def factory_telemetry_topic(factory_id: str) -> str:
    """
    motorguard/factories/FACTORY_001/motors/+/telemetry
    """

    factory_id = validate_topic_component(
        factory_id,
        "factory_id",
    )

    return (
        f"{ROOT_TOPIC}/factories/{factory_id}"
        "/motors/+/telemetry"
    )


def all_telemetry_topic() -> str:
    """
    motorguard/factories/+/motors/+/telemetry
    """

    return f"{ROOT_TOPIC}/factories/+/motors/+/telemetry"
