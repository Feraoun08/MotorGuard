import logging
from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS

logger = logging.getLogger("motorguard.backend.influx")


class InfluxTelemetryStore:

    MEASUREMENT = "motor_telemetry"

    VIBRATION_FIELDS = (
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

    def __init__(
        self,
        url: str,
        token: str,
        org: str,
        bucket: str,
    ):
        self.org = org
        self.bucket = bucket

        self.client = InfluxDBClient(
            url=url,
            token=token,
            org=org,
            timeout=10_000,
        )

        self.write_api = self.client.write_api(
            write_options=SYNCHRONOUS
        )

        self.query_api = self.client.query_api()

    def write_telemetry(self, payload: dict) -> None:

        timestamp = datetime.fromisoformat(
            payload["timestamp"].replace("Z", "+00:00")
        )

        vibration = payload["vibration"]
        sensors = payload["sensors"]
        simulation = payload["simulation"]

        point = (
            Point(self.MEASUREMENT)
            .tag("factory_id", payload["factory_id"])
            .tag("line_id", payload["line_id"])
            .tag("motor_id", payload["motor_id"])
            .tag("motor_state", payload["motor_state"])
            .tag("bearing_condition", payload["bearing_condition"])
            .tag("ground_truth", payload["ground_truth"])
            .tag(
                "is_simulated",
                str(simulation["is_simulated"]).lower(),
            )
            .time(timestamp)
        )

        for field in self.VIBRATION_FIELDS:
            point = point.field(
                field,
                float(vibration[field]),
            )

        point = (
            point
            .field("temperature", float(sensors["temperature"]))
            .field("current", float(sensors["current"]))
            .field("rpm", float(sensors["rpm"]))
        )

        if simulation.get("vibration_source"):
            point = point.tag(
                "vibration_source",
                str(simulation["vibration_source"]),
            )

        if simulation.get("additional_sensor_source"):
            point = point.tag(
                "additional_sensor_source",
                str(simulation["additional_sensor_source"]),
            )

        self.write_api.write(
            bucket=self.bucket,
            org=self.org,
            record=point,
        )

        logger.info(
            "InfluxDB telemetry persisted | motor=%s | timestamp=%s",
            payload["motor_id"],
            timestamp.isoformat(),
        )

    def health_check(self) -> bool:
        return self.client.ping()

    def close(self):
        self.client.close()