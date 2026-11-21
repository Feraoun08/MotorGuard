
import json
import math
import pytest

from simulator.config import BEARING_CONDITIONS, FEATURE_COLUMNS
from simulator.dataset_provider import DatasetProvider
from simulator.sensors import SensorSimulator
from simulator.telemetry import validate_json_schema
from simulator.telemetry import (
    TelemetryValidationError,
    serialize_telemetry,
    deserialize_telemetry,
    validate_telemetry,
)
from simulator.factory import FactoryEngine


@pytest.fixture
def dataset_provider():
    return DatasetProvider(random_seed=42)


def test_csv_loading(dataset_provider):
    assert dataset_provider is not None


def test_sampling_all_ten_classes(dataset_provider):
    for condition in BEARING_CONDITIONS:
        measurement = dataset_provider.sample(condition)

        assert measurement is not None
        assert measurement.ground_truth == condition


def test_feature_vector_structure(dataset_provider):
    for condition in BEARING_CONDITIONS:
        measurement = dataset_provider.sample(condition)

        assert list(measurement.features.keys()) == FEATURE_COLUMNS
        assert len(measurement.features) == len(FEATURE_COLUMNS)

        for value in measurement.features.values():
            assert isinstance(value, (int, float))
            assert math.isfinite(value)


def test_sensor_generation():
    simulator = SensorSimulator(random_seed=42)

    reading = simulator.generate(
        motor_state=__import__(
            "simulator.config", fromlist=["MotorState"]
        ).MotorState.RUNNING,
        is_faulty=False,
    )

    assert reading.temperature >= 0
    assert reading.current >= 0
    assert reading.rpm >= 0


def test_factory_generates_readings(dataset_provider):
    engine = FactoryEngine(
        dataset_provider=dataset_provider,
        interval_seconds=0.1,
    )

    assert engine is not None


def create_valid_telemetry():
    return {
        "timestamp": "2026-11-21T17:30:00+00:00",
        "motor_id": "MOTOR_001",
        "motor_name": "Motor 001",
        "factory_id": "FACTORY_001",
        "line_id": "LINE_001",
        "motor_state": "RUNNING",
        "bearing_condition": "Normal_1",
        "vibration": {
            "max": 0.42,
            "min": -0.39,
            "mean": 0.01,
            "sd": 0.12,
            "rms": 0.15,
            "skewness": 0.08,
            "kurtosis": 3.1,
            "crest": 2.8,
            "form": 1.2,
        },
        "ground_truth": "Normal_1",
        "sensors": {
            "temperature": 44.8,
            "current": 4.75,
            "rpm": 1748.2,
        },
        "simulation": {
            "is_simulated": True,
            "vibration_source": "CWRU_PREPARED_CSV",
            "additional_sensor_source": "SYNTHETIC",
        },
    }


def test_valid_telemetry():
    reading = create_valid_telemetry()

    validate_telemetry(reading)


def test_telemetry_serialization_roundtrip():
    reading = create_valid_telemetry()

    payload = serialize_telemetry(reading)

    assert isinstance(payload, str)

    decoded = deserialize_telemetry(payload)

    assert decoded["motor_id"] == reading["motor_id"]
    assert decoded["vibration"] == reading["vibration"]
    assert decoded["sensors"] == reading["sensors"]
    assert decoded["schema_version"] == "1.0"


def test_json_is_valid():
    reading = create_valid_telemetry()

    payload = serialize_telemetry(reading)

    decoded = json.loads(payload)

    assert isinstance(decoded, dict)
    assert decoded["motor_id"] == "MOTOR_001"


def test_missing_field_rejected():
    reading = create_valid_telemetry()

    del reading["motor_id"]

    with pytest.raises(TelemetryValidationError):
        validate_telemetry(reading)


def test_invalid_feature_value_rejected():
    reading = create_valid_telemetry()

    reading["vibration"]["rms"] = float("nan")

    with pytest.raises(TelemetryValidationError):
        validate_telemetry(reading)


def test_infinite_sensor_value_rejected():
    reading = create_valid_telemetry()

    reading["sensors"]["rpm"] = float("inf")

    with pytest.raises(TelemetryValidationError):
        validate_telemetry(reading)


def test_invalid_feature_order_rejected():
    reading = create_valid_telemetry()

    reading["vibration"] = dict(
        reversed(list(reading["vibration"].items()))
    )

    with pytest.raises(TelemetryValidationError):
        validate_telemetry(reading)


def test_invalid_motor_state_rejected():
    reading = create_valid_telemetry()

    reading["motor_state"] = "BROKEN_STATE"

    with pytest.raises(TelemetryValidationError):
        validate_telemetry(reading)


def test_invalid_json_rejected():
    with pytest.raises(TelemetryValidationError):
        deserialize_telemetry("{invalid json")
def test_json_schema_accepts_valid_telemetry():
    reading = create_valid_telemetry()

    reading["schema_version"] = "1.0"

    validate_json_schema(reading)


def test_json_schema_rejects_missing_sensor():
    reading = create_valid_telemetry()

    reading["schema_version"] = "1.0"
    del reading["sensors"]["rpm"]

    with pytest.raises(Exception):
        validate_json_schema(reading)


def test_json_schema_rejects_invalid_state():
    reading = create_valid_telemetry()

    reading["schema_version"] = "1.0"
    reading["motor_state"] = "INVALID"

    with pytest.raises(Exception):
        validate_json_schema(reading)