import logging

from backend.ingestion.event_key import generate_event_key
from backend.validation.telemetry_validator import (
    decode_and_validate,
    TelemetryValidationError,
)

logger = logging.getLogger("motorguard.backend.ingestion")


class TelemetryIngestionService:

    def __init__(self, repository):
        self.repository = repository

        self.received_count = 0
        self.accepted_count = 0
        self.duplicate_count = 0
        self.rejected_count = 0
        self.storage_error_count = 0

    def ingest(
        self,
        topic: str,
        raw_payload: bytes,
    ) -> str:

        self.received_count += 1

        try:
            payload = decode_and_validate(
                topic,
                raw_payload,
            )

        except TelemetryValidationError as exc:

            self.rejected_count += 1

            logger.warning(
                "Telemetry rejected | topic=%s | reason=%s",
                topic,
                exc,
            )

            return "rejected"

        event_key = generate_event_key(payload)

        try:
            inserted = self.repository.register_telemetry(
                event_key=event_key,
                topic=topic,
                payload=payload,
            )

        except Exception:

            self.storage_error_count += 1

            logger.exception(
                "PostgreSQL inbox registration failed | "
                "event=%s | topic=%s",
                event_key,
                topic,
            )

            return "database_error"

        if inserted:
            self.accepted_count += 1
            return "accepted"

        self.duplicate_count += 1
        return "duplicate"

    def statistics(self) -> dict:

        return {
            "received": self.received_count,
            "accepted": self.accepted_count,
            "duplicates": self.duplicate_count,
            "rejected": self.rejected_count,
            "storage_errors": self.storage_error_count,
        }