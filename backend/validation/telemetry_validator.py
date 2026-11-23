import json
import math
from datetime import datetime
from typing import Any

from backend.mqtt.topic_parser import parse_telemetry_topic


SUPPORTED_SCHEMA_VERSION = "1.0"

REQUIRED_FIELDS = {
    "schema_version",
    "timestamp",
    "motor_id",
    "motor_name",
    "factory_id",
    "line_id",
    "motor_state",
    "bearing_condition",
    "vibration",
    "ground_truth",
    "sensors",
    "simulation",
}

VIBRATION_FIELDS = {
    "max",
    "min",
    "mean",
    "sd",
    "rms",
    "skewness",
    "kurtosis",
    "crest",
    "form",
}

SENSOR_FIELDS = {
    "temperature",
    "current",
    "rpm",
}

VALID_MOTOR_STATES = {
    "STOPPED",
    "RUNNING",
    "WARNING",
    "FAULT",
}


class TelemetryValidationError(ValueError):
    pass


def _require_string(
    payload: dict[str, Any],
    field: str,
) -> None:
    value = payload.get(field)

    if not isinstance(value, str) or not value.strip():
        raise TelemetryValidationError(
            f"{field} must be a non-empty string"
        )


def _require_finite_number(
    value: Any,
    field: str,
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TelemetryValidationError(
            f"{field} must be numeric"
        )

    value = float(value)

    if not math.isfinite(value):
        raise TelemetryValidationError(
            f"{field} must be finite"
        )

    return value


def _validate_timestamp(value: Any) -> datetime:
    if not isinstance(value, str):
        raise TelemetryValidationError(
            "timestamp must be a string"
        )

    try:
        timestamp = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise TelemetryValidationError(
            "timestamp must be a valid ISO-8601 timestamp"
        ) from exc

    if timestamp.tzinfo is None:
        raise TelemetryValidationError(
            "timestamp must include timezone information"
        )

    return timestamp


def validate_telemetry(
    topic: str,
    payload: dict[str, Any],
) -> dict[str, Any]:

    if not isinstance(payload, dict):
        raise TelemetryValidationError(
            "Telemetry payload must be a JSON object"
        )

    missing = REQUIRED_FIELDS - payload.keys()

    if missing:
        raise TelemetryValidationError(
            f"Missing required fields: {sorted(missing)}"
        )

    if payload["schema_version"] != SUPPORTED_SCHEMA_VERSION:
        raise TelemetryValidationError(
            f"Unsupported schema version: "
            f"{payload['schema_version']!r}"
        )

    _validate_timestamp(payload["timestamp"])

    for field in (
        "motor_id",
        "motor_name",
        "factory_id",
        "line_id",
        "bearing_condition",
        "ground_truth",
    ):
        _require_string(payload, field)

    if payload["motor_state"] not in VALID_MOTOR_STATES:
        raise TelemetryValidationError(
            f"Invalid motor state: {payload['motor_state']!r}"
        )

    topic_ids = parse_telemetry_topic(topic)

    if topic_ids.factory_id != payload["factory_id"]:
        raise TelemetryValidationError(
            "Factory ID mismatch between MQTT topic and payload"
        )

    if topic_ids.motor_id != payload["motor_id"]:
        raise TelemetryValidationError(
            "Motor ID mismatch between MQTT topic and payload"
        )

    vibration = payload["vibration"]

    if not isinstance(vibration, dict):
        raise TelemetryValidationError(
            "vibration must be an object"
        )

    missing_vibration = VIBRATION_FIELDS - vibration.keys()

    if missing_vibration:
        raise TelemetryValidationError(
            f"Missing vibration fields: "
            f"{sorted(missing_vibration)}"
        )

    for field in VIBRATION_FIELDS:
        vibration[field] = _require_finite_number(
            vibration[field],
            f"vibration.{field}",
        )

    sensors = payload["sensors"]

    if not isinstance(sensors, dict):
        raise TelemetryValidationError(
            "sensors must be an object"
        )

    missing_sensors = SENSOR_FIELDS - sensors.keys()

    if missing_sensors:
        raise TelemetryValidationError(
            f"Missing sensor fields: {sorted(missing_sensors)}"
        )

    for field in SENSOR_FIELDS:
        sensors[field] = _require_finite_number(
            sensors[field],
            f"sensors.{field}",
        )

        if sensors[field] < 0:
            raise TelemetryValidationError(
                f"sensors.{field} cannot be negative"
            )

    simulation = payload["simulation"]

    if not isinstance(simulation, dict):
        raise TelemetryValidationError(
            "simulation must be an object"
        )

    if "is_simulated" not in simulation:
        raise TelemetryValidationError(
            "simulation.is_simulated is required"
        )

    if not isinstance(simulation["is_simulated"], bool):
        raise TelemetryValidationError(
            "simulation.is_simulated must be boolean"
        )

    return payload


def decode_and_validate(
    topic: str,
    raw_payload: bytes,
) -> dict[str, Any]:

    try:
        decoded = raw_payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TelemetryValidationError(
            "Payload is not valid UTF-8"
        ) from exc

    try:
        payload = json.loads(decoded)
    except json.JSONDecodeError as exc:
        raise TelemetryValidationError(
            f"Invalid JSON payload: {exc}"
        ) from exc

    return validate_telemetry(topic, payload)