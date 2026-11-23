
import logging
import sys

from backend.config import load_settings
from backend.logging_config import configure_logging


def main() -> None:
    try:
        settings = load_settings()
    except (ValueError, TypeError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        sys.exit(1)

    configure_logging(settings.log_level)

    logger = logging.getLogger("backend")

    logger.info("MotorGuard backend starting")
    logger.info(
        "MQTT broker: %s:%s",
        settings.mqtt_broker_host,
        settings.mqtt_broker_port,
    )
    logger.info("MQTT topic: %s", settings.mqtt_topic)
    logger.info(
        "PostgreSQL target: %s:%s/%s",
        settings.postgres_host,
        settings.postgres_port,
        settings.postgres_db,
    )
    logger.info("InfluxDB URL: %s", settings.influx_url)

    # Phase 4 services will be initialized here in subsequent
    # implementation steps:
    #
    # 1. PostgreSQL engine and session factory
    # 2. InfluxDB client
    # 3. MQTT consumer
    # 4. Durable ingestion service
    # 5. Ingestion worker

    logger.info("Configuration validated successfully")
    logger.info("Backend foundation initialized")


if __name__ == "__main__":
    main()
