from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.api.services.factory_service import FactoryService


class TelemetryService:
    """
    Service for retrieving motor telemetry.
    """

    def __init__(
        self,
        session: Session,
        influx_store,
    ):
        self.factory_service = FactoryService(session)
        self.influx_store = influx_store

    @staticmethod
    def _convert_record(record: dict) -> dict:
        """
        Convert an InfluxDB record to the API response format.
        """

        timestamp = record.get("_time")

        if isinstance(timestamp, datetime):
            timestamp = timestamp.isoformat()

        vibration_fields = (
            "max",
            "min",
            "mean",
            "sd",
            "rms",
            "skewness",
            "kurtosis",
            "crest",
            "form",
        )

        sensor_fields = (
            "temperature",
            "current",
            "rpm",
        )

        vibration = {
            field: record[field]
            for field in vibration_fields
            if field in record and record[field] is not None
        }

        sensors = {
            field: record[field]
            for field in sensor_fields
            if field in record and record[field] is not None
        }

        known_fields = {
            "_time",
            "_measurement",
            "_start",
            "_stop",
            "factory_id",
            "line_id",
            "motor_id",
            "motor_state",
            "bearing_condition",
            "ground_truth",
            "is_simulated",
            *vibration_fields,
            *sensor_fields,
            "vibration_source",
            "additional_sensor_source",
        }

        additional_tags = {
            key: value
            for key, value in record.items()
            if key not in known_fields and value is not None
        }

        return {
            "factory_id": record.get("factory_id"),
            "line_id": record.get("line_id"),
            "motor_id": record.get("motor_id"),
            "timestamp": timestamp,
            "motor_state": record.get("motor_state"),
            "bearing_condition": record.get("bearing_condition"),
            "ground_truth": record.get("ground_truth"),
            "is_simulated": record.get("is_simulated"),
            "vibration": vibration,
            "sensors": sensors,
            "additional_tags": additional_tags,
        }

    def get_latest(
        self,
        factory_id: str,
        motor_id: str,
    ) -> dict | None:

        self.factory_service.get_motor(
            factory_id,
            motor_id,
        )

        record = self.influx_store.get_latest_motor_telemetry(
            factory_id,
            motor_id,
        )

        if record is None:
            return None

        return self._convert_record(record)

    def get_history(
        self,
        factory_id: str,
        motor_id: str,
        start: datetime,
        end: datetime,
        limit: int,
    ) -> list[dict]:

        self.factory_service.get_motor(
            factory_id,
            motor_id,
        )

        records = self.influx_store.query_motor_telemetry(
            factory_id=factory_id,
            motor_id=motor_id,
            start=f'time(v: "{start.astimezone(timezone.utc).isoformat()}")',
            end=f'time(v: "{end.astimezone(timezone.utc).isoformat()}")',
            limit=limit,
        )

        return [
            self._convert_record(record)
            for record in records
        ]