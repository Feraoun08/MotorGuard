
from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from backend.api.services.telemetry_service import TelemetryService


@pytest.fixture
def influx_store():
    return Mock()


@pytest.fixture
def telemetry_service(monkeypatch, influx_store):
    # Mock motor existence validation to isolate telemetry tests.
    factory_service = Mock()
    factory_service.get_motor.return_value = object()

    monkeypatch.setattr(
        "backend.api.services.telemetry_service.FactoryService",
        lambda session: factory_service,
    )

    service = TelemetryService(
        session=Mock(),
        influx_store=influx_store,
    )

    service.factory_service = factory_service

    return service


@pytest.fixture
def sample_record():
    return {
        "_time": datetime(
            2026, 11, 25, 18, 0, 0,
            tzinfo=timezone.utc,
        ),
        "_measurement": "motor_telemetry",
        "factory_id": "factory-01",
        "line_id": "line-01",
        "motor_id": "motor-01",
        "motor_state": "running",
        "bearing_condition": "normal",
        "ground_truth": "normal",
        "is_simulated": "true",
        "max": 5.2,
        "min": -4.8,
        "mean": 0.1,
        "sd": 1.2,
        "rms": 2.4,
        "skewness": 0.3,
        "kurtosis": 3.1,
        "crest": 2.8,
        "form": 1.7,
        "temperature": 45.5,
        "current": 2.1,
        "rpm": 1450,
        "vibration_source": "synthetic",
        "additional_sensor_source": "synthetic",
    }


# ---------------------------------------------------------
# LATEST TELEMETRY
# ---------------------------------------------------------


def test_get_latest_returns_converted_telemetry(
    telemetry_service,
    influx_store,
    sample_record,
):
    influx_store.get_latest_motor_telemetry.return_value = sample_record

    result = telemetry_service.get_latest(
        factory_id="factory-01",
        motor_id="motor-01",
    )

    assert result is not None
    assert result["factory_id"] == "factory-01"
    assert result["line_id"] == "line-01"
    assert result["motor_id"] == "motor-01"
    assert result["motor_state"] == "running"

    assert result["vibration"]["rms"] == 2.4
    assert result["vibration"]["max"] == 5.2
    assert result["vibration"]["min"] == -4.8

    assert result["sensors"]["temperature"] == 45.5
    assert result["sensors"]["current"] == 2.1
    assert result["sensors"]["rpm"] == 1450

    assert result["additional_tags"] == {}

    influx_store.get_latest_motor_telemetry.assert_called_once_with(
        "factory-01",
        "motor-01",
    )


def test_get_latest_returns_none_when_no_telemetry(
    telemetry_service,
    influx_store,
):
    influx_store.get_latest_motor_telemetry.return_value = None

    result = telemetry_service.get_latest(
        factory_id="factory-01",
        motor_id="motor-01",
    )

    assert result is None


def test_get_latest_does_not_query_influx_for_unknown_motor(
    telemetry_service,
    influx_store,
):
    telemetry_service.factory_service.get_motor.side_effect = (
        LookupError("Motor not found")
    )

    with pytest.raises(LookupError, match="Motor not found"):
        telemetry_service.get_latest(
            factory_id="factory-01",
            motor_id="motor-999",
        )

    influx_store.get_latest_motor_telemetry.assert_not_called()


# ---------------------------------------------------------
# TELEMETRY CONVERSION
# ---------------------------------------------------------


def test_convert_record_handles_missing_optional_fields():
    record = {
        "_time": datetime(
            2026, 11, 25, 18, 0, 0,
            tzinfo=timezone.utc,
        ),
        "factory_id": "factory-01",
        "line_id": "line-01",
        "motor_id": "motor-01",
        "motor_state": "running",
        "bearing_condition": "normal",
        "ground_truth": "normal",
        "is_simulated": "true",
        "rms": 2.4,
        "temperature": 45.5,
        "custom_tag": "test-value",
    }

    result = TelemetryService._convert_record(record)

    assert result["vibration"] == {"rms": 2.4}
    assert result["sensors"] == {"temperature": 45.5}
    assert result["additional_tags"] == {"custom_tag": "test-value"}

    assert "max" not in result["vibration"]
    assert "rpm" not in result["sensors"]


def test_convert_record_converts_datetime_to_iso_string(
    sample_record,
):
    result = TelemetryService._convert_record(sample_record)

    assert isinstance(result["timestamp"], str)
    assert result["timestamp"] == (
        "2026-11-25T18:00:00+00:00"
    )


# ---------------------------------------------------------
# TELEMETRY HISTORY
# ---------------------------------------------------------


def test_get_history_returns_converted_records(
    telemetry_service,
    influx_store,
    sample_record,
):
    influx_store.query_motor_telemetry.return_value = [
        sample_record,
    ]

    start = datetime(
        2026, 11, 25, 17, 0, 0,
        tzinfo=timezone.utc,
    )

    end = datetime(
        2026, 11, 25, 19, 0, 0,
        tzinfo=timezone.utc,
    )

    result = telemetry_service.get_history(
        factory_id="factory-01",
        motor_id="motor-01",
        start=start,
        end=end,
        limit=100,
    )

    assert len(result) == 1
    assert result[0]["motor_id"] == "motor-01"
    assert result[0]["vibration"]["rms"] == 2.4

    influx_store.query_motor_telemetry.assert_called_once()

    call_args = influx_store.query_motor_telemetry.call_args.kwargs

    assert call_args["factory_id"] == "factory-01"
    assert call_args["motor_id"] == "motor-01"
    assert call_args["limit"] == 100
    assert call_args["start"].startswith('time(v: "')
    assert call_args["end"].startswith('time(v: "')


def test_get_history_returns_empty_list_when_no_records(
    telemetry_service,
    influx_store,
):
    influx_store.query_motor_telemetry.return_value = []

    start = datetime(
        2026, 11, 25, 17, 0, 0,
        tzinfo=timezone.utc,
    )

    end = datetime(
        2026, 11, 25, 19, 0, 0,
        tzinfo=timezone.utc,
    )

    result = telemetry_service.get_history(
        factory_id="factory-01",
        motor_id="motor-01",
        start=start,
        end=end,
        limit=100,
    )

    assert result == []


def test_get_history_does_not_query_influx_for_unknown_motor(
    telemetry_service,
    influx_store,
):
    telemetry_service.factory_service.get_motor.side_effect = (
        LookupError("Motor not found")
    )

    start = datetime(
        2026, 11, 25, 17, 0, 0,
        tzinfo=timezone.utc,
    )

    end = datetime(
        2026, 11, 25, 19, 0, 0,
        tzinfo=timezone.utc,
    )

    with pytest.raises(LookupError, match="Motor not found"):
        telemetry_service.get_history(
            factory_id="factory-01",
            motor_id="motor-999",
            start=start,
            end=end,
            limit=100,
        )

    influx_store.query_motor_telemetry.assert_not_called()
