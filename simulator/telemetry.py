
import json
import math
from datetime import datetime
from typing import Any
from pathlib import Path
from jsonschema import Draft202012Validator
FEATURE_COLUMNS = [
    "max",
    "min",
    "mean",
    "sd",
    "rms",
    "skewness",
    "kurtosis",
    "crest",
    "form",
]

TELEMETRY_SCHEMA_VERSION = "1.0"


class TelemetryValidationError(ValueError):
    """Raised when telemetry does not satisfy the required contract."""


def _is_finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate_telemetry(reading: dict) -> None:
    """Validate a telemetry message against the simulator contract."""

    required_fields = {
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

    missing = required_fields - reading.keys()

    if missing:
        raise TelemetryValidationError(
            f"Missing telemetry fields: {sorted(missing)}"
        )

    # Timestamp validation
    try:
        datetime.fromisoformat(reading["timestamp"].replace("Z", "+00:00"))
    except (TypeError, ValueError, AttributeError):
        raise TelemetryValidationError("Invalid timestamp format")

    # Identifier validation
    for field in ("motor_id", "motor_name", "factory_id", "line_id"):
        if not isinstance(reading[field], str) or not reading[field].strip():
            raise TelemetryValidationError(
                f"{field} must be a non-empty string"
            )

    # Motor state validation
    allowed_states = {"STOPPED", "RUNNING", "WARNING", "FAULT"}

    if reading["motor_state"] not in allowed_states:
        raise TelemetryValidationError(
            f"Invalid motor state: {reading['motor_state']}"
        )

    # Vibration feature validation
    vibration = reading["vibration"]

    if not isinstance(vibration, dict):
        raise TelemetryValidationError("vibration must be a dictionary")

    if list(vibration.keys()) != FEATURE_COLUMNS:
        raise TelemetryValidationError(
            "Vibration feature names or order do not match the model contract"
        )

    for feature, value in vibration.items():
        if not _is_finite_number(value):
            raise TelemetryValidationError(
                f"Invalid vibration feature '{feature}': {value}"
            )

    # Synthetic sensor validation
    sensors = reading["sensors"]

    required_sensors = {"temperature", "current", "rpm"}

    if not isinstance(sensors, dict) or not required_sensors.issubset(sensors):
        raise TelemetryValidationError(
            "Sensor structure must contain temperature, current and rpm"
        )

    for sensor, value in sensors.items():
        if not _is_finite_number(value):
            raise TelemetryValidationError(
                f"Invalid sensor value for '{sensor}'"
            )

    if sensors["temperature"] < 0:
        raise TelemetryValidationError("Temperature cannot be negative")

    if sensors["current"] < 0:
        raise TelemetryValidationError("Current cannot be negative")

    if sensors["rpm"] < 0:
        raise TelemetryValidationError("RPM cannot be negative")

    # Simulation metadata
    simulation = reading["simulation"]

    if not isinstance(simulation, dict):
        raise TelemetryValidationError(
            "simulation metadata must be a dictionary"
        )

    if "is_simulated" not in simulation:
        raise TelemetryValidationError(
            "simulation metadata must include is_simulated"
        )

    if not isinstance(simulation["is_simulated"], bool):
        raise TelemetryValidationError(
            "is_simulated must be boolean"
        )


def create_telemetry(reading: dict) -> dict:
    
    telemetry = {
        "schema_version": TELEMETRY_SCHEMA_VERSION,
        **reading,
    }

    validate_telemetry(telemetry)
    validate_json_schema(telemetry)

    return telemetry


def serialize_telemetry(reading: dict) -> str:
    """Convert validated telemetry into a JSON string."""

    telemetry = create_telemetry(reading)

    return json.dumps(
        telemetry,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    )


def deserialize_telemetry(payload: str) -> dict:
    """Decode JSON and validate its telemetry structure."""

    try:
        reading = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise TelemetryValidationError(
            "Invalid JSON telemetry payload"
        ) from exc

    if not isinstance(reading, dict):
        raise TelemetryValidationError(
            "Telemetry payload must be a JSON object"
        )

    if reading.get("schema_version") != TELEMETRY_SCHEMA_VERSION:
        raise TelemetryValidationError(
            "Unsupported telemetry schema version"
        )

    validate_telemetry(reading)

    return reading
def validate_json_schema(reading: dict) -> None:
    """Validate telemetry using the formal JSON Schema."""

    schema_path = Path(__file__).resolve().parent / "telemetry_schema.json"

    with schema_path.open("r", encoding="utf-8") as file:
        schema = json.load(file)

    validator = Draft202012Validator(schema)

    errors = sorted(
        validator.iter_errors(reading),
        key=lambda error: list(error.path),
    )

    if errors:
        details = "\n".join(
            f"{list(error.path)}: {error.message}"
            for error in errors
        )

        raise TelemetryValidationError(
            f"JSON Schema validation failed:\n{details}"
        )
