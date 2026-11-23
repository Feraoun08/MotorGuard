import pytest

from backend.mqtt.topic_parser import (
    parse_telemetry_topic,
)


def test_valid_topic():

    result = parse_telemetry_topic(
        "motorguard/factories/FACTORY_01/"
        "motors/MOTOR_01/telemetry"
    )

    assert result.factory_id == "FACTORY_01"
    assert result.motor_id == "MOTOR_01"


def test_invalid_topic():

    with pytest.raises(ValueError):
        parse_telemetry_topic(
            "motorguard/invalid/topic"
        )


def test_topic_with_invalid_motor_identifier():

    with pytest.raises(ValueError):
        parse_telemetry_topic(
            "motorguard/factories/FACTORY_01/"
            "motors/MOTOR%201/telemetry"
        )


def test_topic_with_wrong_root():

    with pytest.raises(ValueError):
        parse_telemetry_topic(
            "other/factories/FACTORY_01/"
            "motors/MOTOR_01/telemetry"
        )