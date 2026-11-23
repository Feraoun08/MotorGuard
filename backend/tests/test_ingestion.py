import json

from backend.ingestion.service import (
    TelemetryIngestionService,
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
    },
}


class FakeRepository:

    def __init__(self, inserted=True):
        self.inserted = inserted
        self.calls = []

    def register_telemetry(
        self,
        event_key,
        topic,
        payload,
    ):
        self.calls.append(
            {
                "event_key": event_key,
                "topic": topic,
                "payload": payload,
            }
        )

        return self.inserted


def test_valid_message_accepted():

    repository = FakeRepository(
        inserted=True,
    )

    service = TelemetryIngestionService(
        repository,
    )

    outcome = service.ingest(
        VALID_TOPIC,
        json.dumps(VALID_PAYLOAD).encode(),
    )

    assert outcome == "accepted"
    assert len(repository.calls) == 1


def test_duplicate_message_detected():

    repository = FakeRepository(
        inserted=False,
    )

    service = TelemetryIngestionService(
        repository,
    )

    outcome = service.ingest(
        VALID_TOPIC,
        json.dumps(VALID_PAYLOAD).encode(),
    )

    assert outcome == "duplicate"
    assert service.duplicate_count == 1


def test_invalid_message_rejected():

    repository = FakeRepository()

    service = TelemetryIngestionService(
        repository,
    )

    outcome = service.ingest(
        VALID_TOPIC,
        b"invalid-json",
    )

    assert outcome == "rejected"
    assert service.rejected_count == 1
    assert len(repository.calls) == 0


def test_database_failure_not_acknowledgeable():

    class FailingRepository:

        def register_telemetry(
            self,
            event_key,
            topic,
            payload,
        ):
            raise RuntimeError(
                "PostgreSQL unavailable"
            )

    service = TelemetryIngestionService(
        FailingRepository(),
    )

    outcome = service.ingest(
        VALID_TOPIC,
        json.dumps(VALID_PAYLOAD).encode(),
    )

    assert outcome == "database_error"
    assert service.storage_error_count == 1