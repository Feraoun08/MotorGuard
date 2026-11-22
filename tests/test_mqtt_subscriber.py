
import json
from types import SimpleNamespace

from communication.mqtt_config import MQTTConfig
from communication.mqtt_subscriber import MQTTSubscriber


def create_subscriber():
    config = MQTTConfig(
        host="localhost",
        port=1883,
        client_id="subscriber_test",
    )

    return MQTTSubscriber(config)


def valid_payload():
    return {
        "schema_version": "1.0",
        "timestamp": "2026-11-22T10:00:00+00:00",
        "motor_id": "MOTOR_001",
        "motor_name": "Test Motor",
        "factory_id": "FACTORY_01",
        "line_id": "LINE_01",
        "motor_state": "RUNNING",
        "bearing_condition": "Normal_1",
        "vibration": {
            "max": 1.0,
            "min": 0.1,
            "mean": 0.5,
            "sd": 0.2,
            "rms": 0.6,
            "skewness": 0.1,
            "kurtosis": 2.0,
            "crest": 1.5,
            "form": 1.2,
        },
        "ground_truth": "Normal_1",
        "sensors": {
            "temperature": 30.0,
            "current": 1.0,
            "rpm": 1500.0,
        },
        "simulation": {
            "is_simulated": True,
            "vibration_source": "CWRU_PREPARED_CSV",
            "additional_sensor_source": "SYNTHETIC",
        },
    }


def make_message(topic, payload):
    return SimpleNamespace(
        topic=topic,
        payload=payload,
    )


VALID_TOPIC = (
    "motorguard/factories/FACTORY_01/"
    "motors/MOTOR_001/telemetry"
)


def test_valid_topic():
    subscriber = create_subscriber()

    factory_id, motor_id = subscriber._validate_topic(
        VALID_TOPIC
    )

    assert factory_id == "FACTORY_01"
    assert motor_id == "MOTOR_001"


def test_invalid_topic_structure():
    subscriber = create_subscriber()

    try:
        subscriber._validate_topic(
            "invalid/topic"
        )
        assert False, "Expected ValueError"

    except ValueError:
        pass


def test_invalid_factory_component():
    subscriber = create_subscriber()

    try:
        subscriber._validate_topic(
            "motorguard/factories/INVALID!/motors/"
            "MOTOR_001/telemetry"
        )
        assert False, "Expected ValueError"

    except ValueError:
        pass


def test_valid_message():
    subscriber = create_subscriber()

    payload = json.dumps(valid_payload()).encode("utf-8")

    message = make_message(
        VALID_TOPIC,
        payload,
    )

    subscriber._on_message(
        None,
        None,
        message,
    )

    assert subscriber.received_count == 1
    assert subscriber.valid_count == 1
    assert subscriber.invalid_count == 0


def test_malformed_json():
    subscriber = create_subscriber()

    message = make_message(
        VALID_TOPIC,
        b"{invalid-json",
    )

    subscriber._on_message(
        None,
        None,
        message,
    )

    assert subscriber.received_count == 1
    assert subscriber.invalid_count == 1
    assert subscriber.json_error_count == 1


def test_invalid_utf8():
    subscriber = create_subscriber()

    message = make_message(
        VALID_TOPIC,
        b"\xff\xfe\xfa",
    )

    subscriber._on_message(
        None,
        None,
        message,
    )

    assert subscriber.received_count == 1
    assert subscriber.invalid_count == 1
    assert subscriber.json_error_count == 1


def test_wrong_topic():
    subscriber = create_subscriber()

    message = make_message(
        "invalid/topic",
        json.dumps(valid_payload()).encode("utf-8"),
    )

    subscriber._on_message(
        None,
        None,
        message,
    )

    assert subscriber.received_count == 1
    assert subscriber.invalid_count == 1
    assert subscriber.topic_error_count == 1


def test_invalid_motor_state():
    subscriber = create_subscriber()

    payload = valid_payload()
    payload["motor_state"] = "UNKNOWN"

    message = make_message(
        VALID_TOPIC,
        json.dumps(payload).encode("utf-8"),
    )

    subscriber._on_message(
        None,
        None,
        message,
    )

    assert subscriber.invalid_count == 1
    assert subscriber.telemetry_error_count == 1


def test_missing_telemetry_field():
    subscriber = create_subscriber()

    payload = valid_payload()
    payload.pop("vibration")

    message = make_message(
        VALID_TOPIC,
        json.dumps(payload).encode("utf-8"),
    )

    subscriber._on_message(
        None,
        None,
        message,
    )

    assert subscriber.invalid_count == 1
    assert subscriber.telemetry_error_count == 1


def test_motor_id_mismatch():
    subscriber = create_subscriber()

    payload = valid_payload()
    payload["motor_id"] = "MOTOR_999"

    message = make_message(
        VALID_TOPIC,
        json.dumps(payload).encode("utf-8"),
    )

    subscriber._on_message(
        None,
        None,
        message,
    )

    assert subscriber.invalid_count == 1
    assert subscriber.telemetry_error_count == 1


def test_factory_id_mismatch():
    subscriber = create_subscriber()

    payload = valid_payload()
    payload["factory_id"] = "FACTORY_999"

    message = make_message(
        VALID_TOPIC,
        json.dumps(payload).encode("utf-8"),
    )

    subscriber._on_message(
        None,
        None,
        message,
    )

    assert subscriber.invalid_count == 1
    assert subscriber.telemetry_error_count == 1


def test_statistics():
    subscriber = create_subscriber()

    valid_message = make_message(
        VALID_TOPIC,
        json.dumps(valid_payload()).encode("utf-8"),
    )

    invalid_message = make_message(
        "bad/topic",
        b"{}",
    )

    subscriber._on_message(None, None, valid_message)
    subscriber._on_message(None, None, invalid_message)

    stats = subscriber.get_statistics()

    assert stats["received"] == 2
    assert stats["valid"] == 1
    assert stats["invalid"] == 1
    assert stats["topic_errors"] == 1
