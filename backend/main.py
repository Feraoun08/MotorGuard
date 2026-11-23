import logging
import signal
import threading

from backend.config import BackendConfig
from backend.logging_config import configure_logging

from backend.database.models import Base
from backend.database.postgres import (
    create_postgres_engine,
    create_session_factory,
)
from backend.database.repositories import TelemetryRepository
from backend.database.influx import InfluxTelemetryStore

from backend.ingestion.service import TelemetryIngestionService
from backend.ingestion.inbox_worker import InboxWorker
from backend.mqtt.consumer import BackendMQTTConsumer


logger = logging.getLogger("motorguard.backend")


def main():

    configure_logging()

    config = BackendConfig.from_env()

    logger.info("Starting MotorGuard Backend Phase 4")

    # PostgreSQL
    engine = create_postgres_engine(config)
    session_factory = create_session_factory(engine)

    # Initial development bootstrap.
    # In a later schema-management step, this is replaced
    # by Alembic migrations.
    Base.metadata.create_all(engine)

    repository = TelemetryRepository(
        session_factory,
    )

    repository.health_check()

    logger.info("PostgreSQL connection successful")

    # InfluxDB
    influx_store = InfluxTelemetryStore(
        url=config.influx_url,
        token=config.influx_token,
        org=config.influx_org,
        bucket=config.influx_bucket,
    )

    if not influx_store.health_check():
        raise RuntimeError(
            "InfluxDB health check failed"
        )

    logger.info("InfluxDB connection successful")

    # Durable inbox worker
    worker = InboxWorker(
        repository=repository,
        influx_store=influx_store,
        poll_interval=config.worker_poll_interval,
        batch_size=config.worker_batch_size,
        max_attempts=config.worker_max_attempts,
    )

    # MQTT ingestion service
    ingestion_service = TelemetryIngestionService(
        repository,
    )

    # Independent MQTT consumer
    consumer = BackendMQTTConsumer(
        config=config,
        ingestion_service=ingestion_service,
    )

    stop_event = threading.Event()

    def shutdown_handler(signum, frame):
        logger.info("Shutdown signal received")
        stop_event.set()

    signal.signal(
        signal.SIGINT,
        shutdown_handler,
    )

    if hasattr(signal, "SIGTERM"):
        signal.signal(
            signal.SIGTERM,
            shutdown_handler,
        )

    try:

        worker.start()

        connected = consumer.connect()

        if not connected:
            raise RuntimeError(
                "Backend MQTT consumer could not connect"
            )

        logger.info(
            "MotorGuard Phase 4 backend is running"
        )

        while not stop_event.wait(timeout=1):

            if not consumer.is_connected:
                logger.warning(
                    "Backend MQTT connection is currently down"
                )

    except KeyboardInterrupt:
        logger.info("Keyboard interruption")

    finally:

        logger.info("Backend shutdown sequence")

        consumer.disconnect()
        worker.stop()
        influx_store.close()
        engine.dispose()

        logger.info(
            "Final ingestion statistics: %s",
            ingestion_service.statistics(),
        )

        logger.info(
            "MotorGuard backend stopped cleanly"
        )


if __name__ == "__main__":
    main()