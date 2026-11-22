
import pytest

from communication.mqtt_topics import (
    telemetry_topic,
    factory_telemetry_topic,
    all_telemetry_topic,
    validate_topic_component,
)


def test_motor_telemetry_topic():
    topic = telemetry_topic("FACTORY_01", "MOTOR_001")

    assert topic == (
        "motorguard/factories/FACTORY_01/"
        "motors/MOTOR_001/telemetry"
    )


def test_factory_wildcard_topic():
    topic = factory_telemetry_topic("FACTORY_01")

    assert topic == (
        "motorguard/factories/FACTORY_01/"
        "motors/+/telemetry"
    )


def test_all_factory_wildcard_topic():
    assert all_telemetry_topic() == (
        "motorguard/factories/+/motors/+/telemetry"
    )


@pytest.mark.parametrize(
    "invalid_component",
    [
        "",
        " ",
        "MOTOR/001",
        "MOTOR+001",
        "MOTOR#001",
        "MOTOR 001",
    ],
)
def test_invalid_topic_components(invalid_component):
    with pytest.raises((ValueError, TypeError)):
        validate_topic_component(
            invalid_component,
            "motor_id",
        )


def test_valid_component():
    assert validate_topic_component(
        "MOTOR_001",
        "motor_id",
    ) == "MOTOR_001"
