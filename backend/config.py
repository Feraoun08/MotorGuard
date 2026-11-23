
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env from the project root
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    
    # MQTT configuration
    
    mqtt_broker_host: str
    mqtt_broker_port: int
    mqtt_username: str | None
    mqtt_password: str | None
    mqtt_client_id: str
    mqtt_topic: str
    mqtt_keepalive: int

    
    # PostgreSQL configuration
    
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str

    
    # InfluxDB configuration
    
    influx_url: str
    influx_token: str
    influx_org: str
    influx_bucket: str

    
    # Backend configuration
    
    log_level: str
    worker_poll_interval: float
    worker_batch_size: int
    worker_max_retries: int

    @property
    def postgres_url(self) -> str:
        """
        SQLAlchemy connection URL.

        Uses psycopg 3 as the PostgreSQL driver.
        """
        return (
            f"postgresql+psycopg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}"
            f"/{self.postgres_db}"
        )


def _required_env(name: str) -> str:
    value = os.getenv(name)

    if value is None or not value.strip():
        raise ValueError(
            f"Missing required environment variable: {name}"
        )

    return value.strip()


def _optional_env(name: str) -> str | None:
    value = os.getenv(name)

    if value is None or not value.strip():
        return None

    return value.strip()


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)

    if value is None or not value.strip():
        return default

    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(
            f"Environment variable {name} must be an integer."
        ) from exc


def _float_env(name: str, default: float) -> float:
    value = os.getenv(name)

    if value is None or not value.strip():
        return default

    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(
            f"Environment variable {name} must be a number."
        ) from exc


def load_settings() -> Settings:
    """
    Load and validate backend configuration.
    """

    settings = Settings(
        # MQTT
        mqtt_broker_host=_required_env("MQTT_BROKER_HOST"),
        mqtt_broker_port=_int_env("MQTT_BROKER_PORT", 1883),
        mqtt_username=_optional_env("MQTT_USERNAME"),
        mqtt_password=_optional_env("MQTT_PASSWORD"),
        mqtt_client_id=_required_env("MQTT_CLIENT_ID"),
        mqtt_topic=os.getenv(
            "MQTT_TOPIC",
            "motorguard/factories/+/motors/+/telemetry",
        ).strip(),
        mqtt_keepalive=_int_env("MQTT_KEEPALIVE", 60),

        # PostgreSQL
        postgres_host=_required_env("POSTGRES_HOST"),
        postgres_port=_int_env("POSTGRES_PORT", 5432),
        postgres_db=_required_env("POSTGRES_DB"),
        postgres_user=_required_env("POSTGRES_USER"),
        postgres_password=_required_env("POSTGRES_PASSWORD"),

        # InfluxDB
        influx_url=_required_env("INFLUX_URL"),
        influx_token=_required_env("INFLUX_TOKEN"),
        influx_org=_required_env("INFLUX_ORG"),
        influx_bucket=_required_env("INFLUX_BUCKET"),

        # Backend
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        worker_poll_interval=_float_env(
            "WORKER_POLL_INTERVAL", 2.0
        ),
        worker_batch_size=_int_env(
            "WORKER_BATCH_SIZE", 50
        ),
        worker_max_retries=_int_env(
            "WORKER_MAX_RETRIES", 10
        ),
    )

    # Validate MQTT port
    if not 1 <= settings.mqtt_broker_port <= 65535:
        raise ValueError("MQTT_BROKER_PORT must be between 1 and 65535.")

    # Validate PostgreSQL port
    if not 1 <= settings.postgres_port <= 65535:
        raise ValueError("POSTGRES_PORT must be between 1 and 65535.")

    # Validate worker settings
    if settings.worker_poll_interval <= 0:
        raise ValueError("WORKER_POLL_INTERVAL must be positive.")

    if settings.worker_batch_size <= 0:
        raise ValueError("WORKER_BATCH_SIZE must be positive.")

    if settings.worker_max_retries < 1:
        raise ValueError("WORKER_MAX_RETRIES must be at least 1.")

    if settings.log_level not in {
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    }:
        raise ValueError(
            "LOG_LEVEL must be DEBUG, INFO, WARNING, ERROR, or CRITICAL."
        )

    return settings
