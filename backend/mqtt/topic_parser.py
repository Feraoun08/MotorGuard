import re
from dataclasses import dataclass


TELEMETRY_TOPIC_PATTERN = re.compile(
    r"^motorguard/factories/"
    r"(?P<factory_id>[A-Za-z0-9_-]+)/"
    r"motors/(?P<motor_id>[A-Za-z0-9_-]+)/telemetry$"
)


@dataclass(frozen=True)
class ParsedTelemetryTopic:
    factory_id: str
    motor_id: str


def parse_telemetry_topic(topic: str) -> ParsedTelemetryTopic:
    if not isinstance(topic, str):
        raise TypeError("MQTT topic must be a string")

    match = TELEMETRY_TOPIC_PATTERN.fullmatch(topic)

    if not match:
        raise ValueError(f"Invalid telemetry topic: {topic!r}")

    return ParsedTelemetryTopic(
        factory_id=match.group("factory_id"),
        motor_id=match.group("motor_id"),
    )