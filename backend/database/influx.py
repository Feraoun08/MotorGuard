import logging
from datetime import datetime

from influxdb_client import InfluxDBClient, Point
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

   
    # WRITE TELEMETRY
   

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

   
    # QUERY TELEMETRY
   

    @staticmethod
    def _escape_flux_string(value: str) -> str:
        """
        Escape a string before inserting it into a Flux string literal.
        """
        return (
            str(value)
            .replace("\\", "\\\\")
            .replace('"', '\\"')
        )

    def query_motor_telemetry(
        self,
        factory_id: str,
        motor_id: str,
        start: str,
        end: str,
        limit: int = 500,
    ) -> list[dict]:
        """
        Query telemetry history for one motor.

        Parameters
        ----------
        factory_id:
            Factory identifier.
        motor_id:
            Motor identifier.
        start:
            Flux range start expression, e.g. -24h or an ISO timestamp.
        end:
            Flux range stop expression, e.g. now() or an ISO timestamp.
        limit:
            Maximum number of telemetry points.

        Returns
        -------
        list[dict]
            Telemetry records ordered newest first.
        """

        if not 1 <= limit <= 5000:
            raise ValueError("limit must be between 1 and 5000")

        escaped_factory_id = self._escape_flux_string(factory_id)
        escaped_motor_id = self._escape_flux_string(motor_id)

        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: {start}, stop: {end})
          |> filter(fn: (r) => r["_measurement"] == "{self.MEASUREMENT}")
          |> filter(fn: (r) => r["factory_id"] == "{escaped_factory_id}")
          |> filter(fn: (r) => r["motor_id"] == "{escaped_motor_id}")
          |> pivot(
              rowKey: [
                  "_time",
                  "factory_id",
                  "line_id",
                  "motor_id",
                  "motor_state",
                  "bearing_condition",
                  "ground_truth",
                  "is_simulated",
                  "vibration_source",
                  "additional_sensor_source"
              ],
              columnKey: ["_field"],
              valueColumn: "_value"
          )
          |> sort(columns: ["_time"], desc: true)
          |> limit(n: {limit})
        '''

        tables = self.query_api.query(
            query=query,
            org=self.org,
        )

        results = []

        for table in tables:
            for record in table.records:
                results.append(record.values)

        return results

   
    # LATEST TELEMETRY
   

    def get_latest_motor_telemetry(
        self,
        factory_id: str,
        motor_id: str,
    ) -> dict | None:
        """
        Retrieve the latest telemetry point for a motor.
        """

        results = self.query_motor_telemetry(
            factory_id=factory_id,
            motor_id=motor_id,
            start="0",
            end="now()",
            limit=1,
        )

        if not results:
            return None

        return results[0]

   
    # HEALTH CHECK
   

    def health_check(self) -> bool:
        return self.client.ping()

   
    # CLOSE CLIENT
   

    def close(self):
        self.client.close()