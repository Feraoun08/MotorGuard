import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class BackendConfig:
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    mqtt_client_id: str = "motorguard_backend_consumer"
    mqtt_username: str | None = None
    mqtt_password: str | None = None
    mqtt_keepalive: int = 60
    mqtt_qos: int = 1

    postgres_url: str = (
        "postgresql+psycopg://motorguard:motorguard"
        "@localhost:5432/motorguard"
    )

    influx_url: str = "http://localhost:8086"
    influx_token: str = ""
    influx_org: str = "motorguard"
    influx_bucket: str = "motor_telemetry"

    worker_poll_interval: float = 2.0
    worker_batch_size: int = 100
    worker_max_attempts: int = 10
    worker_retry_base_seconds: int = 2
    worker_retry_max_seconds: int = 300
    worker_processing_lease_seconds: int = 120

    def __post_init__(self):
        if not self.mqtt_host.strip():
            raise ValueError("MQTT host cannot be empty")

        if not 1 <= self.mqtt_port <= 65535:
            raise ValueError("Invalid MQTT port")

        if not self.mqtt_client_id.strip():
            raise ValueError("MQTT client ID cannot be empty")

        if not self.postgres_url.strip():
            raise ValueError("PostgreSQL URL cannot be empty")

        if not self.influx_url.strip():
            raise ValueError("InfluxDB URL cannot be empty")

        if not self.influx_org.strip():
            raise ValueError("InfluxDB organization cannot be empty")

        if not self.influx_bucket.strip():
            raise ValueError("InfluxDB bucket cannot be empty")

        if self.worker_poll_interval <= 0:
            raise ValueError("Worker poll interval must be positive")

        if self.worker_batch_size <= 0:
            raise ValueError("Worker batch size must be positive")

        if self.worker_max_attempts <= 0:
            raise ValueError("Worker max attempts must be positive")
        if self.worker_retry_base_seconds <= 0:
           raise ValueError("Worker retry base must be positive")

        if self.worker_retry_max_seconds < self.worker_retry_base_seconds:
          raise ValueError("Worker retry maximum must be >= retry base")

        if self.worker_processing_lease_seconds <= 0:
         raise ValueError("Worker processing lease must be positive")

    @classmethod
    def from_env(cls) -> "BackendConfig":
        return cls(
            mqtt_host=os.getenv("MQTT_HOST", "localhost"),
            mqtt_port=int(os.getenv("MQTT_PORT", "1883")),
            mqtt_client_id=os.getenv(
                "MQTT_BACKEND_CLIENT_ID",
                "motorguard_backend_consumer",
            ),
            mqtt_username=os.getenv("MQTT_USERNAME") or None,
            mqtt_password=os.getenv("MQTT_PASSWORD") or None,
            mqtt_keepalive=int(os.getenv("MQTT_KEEPALIVE", "60")),
            mqtt_qos=int(os.getenv("MQTT_QOS", "1")),
            postgres_url=os.getenv(
                "POSTGRES_URL",
                "postgresql+psycopg://motorguard:motorguard"
                "@localhost:5432/motorguard",
            ),
            influx_url=os.getenv(
                "INFLUX_URL",
                "http://localhost:8086",
            ),
            influx_token=os.getenv("INFLUX_TOKEN", ""),
            influx_org=os.getenv(
                "INFLUX_ORG",
                "motorguard",
            ),
            influx_bucket=os.getenv(
                "INFLUX_BUCKET",
                "motor_telemetry",
            ),
            worker_poll_interval=float(
                os.getenv("WORKER_POLL_INTERVAL", "2")
            ),
            worker_batch_size=int(
                os.getenv("WORKER_BATCH_SIZE", "100")
            ),
            worker_max_attempts=int(
                os.getenv("WORKER_MAX_ATTEMPTS", "10")
            ),
            worker_retry_base_seconds=int(
    os.getenv("WORKER_RETRY_BASE_SECONDS", "2")
),
worker_retry_max_seconds=int(
    os.getenv("WORKER_RETRY_MAX_SECONDS", "300")
),
worker_processing_lease_seconds=int(
    os.getenv("WORKER_PROCESSING_LEASE_SECONDS", "120")
),
        )