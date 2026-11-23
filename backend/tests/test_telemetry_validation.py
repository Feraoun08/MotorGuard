import json
import copy
import pytest

from backend.validation.telemetry_validator import (
    decode_and_validate,
    TelemetryValidationError,
)


VALID_TOPIC = (
    "motorguard/factories/FACTORY_01/"
    "motors/MOTOR_01/telemetry"
)


VALID_PAYLOAD = {
    "schema_version": "1.0",
    "timestamp": "2026-11-23T10:00:00+00:00",
    "motor_id": "MOTOR_01",
    "motor_name": "Motor 01",
    "factory_id": "FACTORY_01",
    "line_id": "LINE_01",
    "motor_state": "RUNNING",
    "bearing_condition": "Normal_1",
    "ground_truth": "Normal_1",
    "vibration": {
        "max": 1.0,
        "min": -1.0,
        "mean": 0.1,
        "sd": 0.2,
        "rms": 0.5,
        "skewness": 0.1,
        "kurtosis": 2.0,
        "crest": 2.0,
        "form": 1.5,
    },
    "sensors": {
        "temperature": 25.0,
        "current": 1.2,
        "rpm": 1500.0,
    },
    "simulation": {
        "is_simulated": True,
        "vibration_source": "dataset",
        "additional_sensor_source": "synthetic",
    },
}


def encode(payload):
    return json.dumps(payload).encode("utf-8")


def test_valid_telemetry():

    payload = copy.deepcopy(VALID_PAYLOAD)

    result = decode_and_validate(
        VALID_TOPIC,
        encode(payload),
    )

    assert result["motor_id"] == "MOTOR_01"
    assert result["factory_id"] == "FACTORY_01"


def test_invalid_json():

    with pytest.raises(TelemetryValidationError):
        decode_and_validate(
            VALID_TOPIC,
            b"{invalid json",
        )


def test_missing_required_field():

    payload = copy.deepcopy(VALID_PAYLOAD)

    del payload["motor_id"]

    with pytest.raises(TelemetryValidationError):
        decode_and_validate(
            VALID_TOPIC,
            encode(payload),
        )


def test_wrong_schema_version():

    payload = copy.deepcopy(VALID_PAYLOAD)

    payload["schema_version"] = "2.0"

    with pytest.raises(TelemetryValidationError):
        decode_and_validate(
            VALID_TOPIC,
            encode(payload),
        )


def test_missing_vibration_feature():

    payload = copy.deepcopy(VALID_PAYLOAD)

    del payload["vibration"]["rms"]

    with pytest.raises(TelemetryValidationError):
        decode_and_validate(
            VALID_TOPIC,
            encode(payload),
        )


def test_nan_is_rejected():

    payload = copy.deepcopy(VALID_PAYLOAD)

    payload["vibration"]["rms"] = float("nan")

    with pytest.raises(TelemetryValidationError):
        decode_and_validate(
            VALID_TOPIC,
            encode(payload),
        )


def test_infinity_is_rejected():

    payload = copy.deepcopy(VALID_PAYLOAD)

    payload["sensors"]["temperature"] = float("inf")

    with pytest.raises(TelemetryValidationError):
        decode_and_validate(
            VALID_TOPIC,
            encode(payload),
        )


def test_naive_timestamp_is_rejected():

    payload = copy.deepcopy(VALID_PAYLOAD)

    payload["timestamp"] = "2026-11-23T10:00:00"

    with pytest.raises(TelemetryValidationError):
        decode_and_validate(
            VALID_TOPIC,
            encode(payload),
        )


def test_negative_sensor_value_is_rejected():

    payload = copy.deepcopy(VALID_PAYLOAD)

    payload["sensors"]["rpm"] = -100

    with pytest.raises(TelemetryValidationError):
        decode_and_validate(
            VALID_TOPIC,
            encode(payload),
        )


def test_motor_topic_payload_mismatch():

    payload = copy.deepcopy(VALID_PAYLOAD)

    payload["motor_id"] = "MOTOR_02"

    with pytest.raises(TelemetryValidationError):
        decode_and_validate(
            VALID_TOPIC,
            encode(payload),
        )


def test_factory_topic_payload_mismatch():

    payload = copy.deepcopy(VALID_PAYLOAD)

    payload["factory_id"] = "FACTORY_02"

    with pytest.raises(TelemetryValidationError):
        decode_and_validate(
            VALID_TOPIC,
            encode(payload),
        )


def test_invalid_motor_state():

    payload = copy.deepcopy(VALID_PAYLOAD)

    payload["motor_state"] = "UNKNOWN"

    with pytest.raises(TelemetryValidationError):
        decode_and_validate(
            VALID_TOPIC,
            encode(payload),
        )