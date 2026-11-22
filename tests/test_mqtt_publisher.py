
import json
from unittest.mock import MagicMock

import paho.mqtt.client as mqtt

from communication.mqtt_config import MQTTConfig
from communication.mqtt_publisher import MQTTPublisher


def create_publisher():
    config = MQTTConfig(
        host="localhost",
        port=1883,
        client_id="publisher_test",
    )
    publisher = MQTTPublisher(config)
    return publisher


def valid_reading():
    return {
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


def test_publisher_initialization():
    publisher = create_publisher()

    assert publisher.config.host == "localhost"
    assert publisher.is_connected is False


def test_publish_when_disconnected():
    publisher = create_publisher()

    result = publisher.publish_reading(valid_reading())

    assert result is False


def test_publish_success(monkeypatch):
    publisher = create_publisher()

    publisher._client_connected = True

    mock_info = MagicMock()
    mock_info.rc = mqtt.MQTT_ERR_SUCCESS
    mock_info.wait_for_publish.return_value = None
    mock_info.is_published.return_value = True

    mock_publish = MagicMock(return_value=mock_info)

    monkeypatch.setattr(
        publisher._client,
        "publish",
        mock_publish,
    )

    result = publisher.publish_reading(valid_reading())

    assert result is True

    mock_publish.assert_called_once()

    kwargs = mock_publish.call_args.kwargs

    assert kwargs["qos"] == 1
    assert kwargs["retain"] is False

    payload = json.loads(kwargs["payload"])

    assert payload["schema_version"] == "1.0"
    assert payload["motor_id"] == "MOTOR_001"


def test_publish_failure_return_code(monkeypatch):
    publisher = create_publisher()
    publisher._client_connected = True

    mock_info = MagicMock()
    mock_info.rc = mqtt.MQTT_ERR_NO_CONN

    monkeypatch.setattr(
        publisher._client,
        "publish",
        MagicMock(return_value=mock_info),
    )

    result = publisher.publish_reading(valid_reading())

    assert result is False


def test_publish_not_confirmed(monkeypatch):
    publisher = create_publisher()
    publisher._client_connected = True

    mock_info = MagicMock()
    mock_info.rc = mqtt.MQTT_ERR_SUCCESS
    mock_info.wait_for_publish.return_value = None
    mock_info.is_published.return_value = False

    monkeypatch.setattr(
        publisher._client,
        "publish",
        MagicMock(return_value=mock_info),
    )

    result = publisher.publish_reading(valid_reading())

    assert result is False


def test_invalid_reading_rejected(monkeypatch):
    publisher = create_publisher()
    publisher._client_connected = True

    invalid = valid_reading()
    invalid["motor_state"] = "UNKNOWN_STATE"

    result = publisher.publish_reading(invalid)

    assert result is False
