import logging
import signal
import threading

from backend.config import BackendConfig
from backend.logging_config import configure_logging

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

    logger.info("Starting MotorGuard Phase 4 Backend")

    engine = create_postgres_engine(config)
    session_factory = create_session_factory(engine)

    repository = TelemetryRepository(
        session_factory,
    )

    repository.health_check()

    logger.info("PostgreSQL health check passed")

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

    logger.info("InfluxDB health check passed")

    ingestion_service = TelemetryIngestionService(
        repository,
    )

    consumer = BackendMQTTConsumer(
        config=config,
        ingestion_service=ingestion_service,
    )

    worker = InboxWorker(
        repository=repository,
        influx_store=influx_store,
        poll_interval=config.worker_poll_interval,
        batch_size=config.worker_batch_size,
        max_attempts=config.worker_max_attempts,
        retry_base_seconds=config.worker_retry_base_seconds,
        retry_max_seconds=config.worker_retry_max_seconds,
        processing_lease_seconds=config.worker_processing_lease_seconds,
    )

    shutdown_event = threading.Event()

    def handle_shutdown(signum, frame):
        logger.info(
            "Shutdown signal received: %s",
            signum,
        )
        shutdown_event.set()

    signal.signal(
        signal.SIGINT,
        handle_shutdown,
    )

    if hasattr(signal, "SIGTERM"):
        signal.signal(
            signal.SIGTERM,
            handle_shutdown,
        )

    try:

        worker.start()

        if not consumer.connect():
            raise RuntimeError(
                "Unable to connect backend MQTT consumer"
            )

        logger.info(
            "MotorGuard Phase 4 backend is running"
        )

        while not shutdown_event.wait(1):

            if not consumer.is_connected:
                logger.warning(
                    "MQTT connection is disconnected; "
                    "automatic reconnect is active"
                )

    except KeyboardInterrupt:
        logger.info("Keyboard interruption received")

    finally:

        logger.info("Beginning backend shutdown")

        consumer.disconnect()
        worker.stop()

        influx_store.close()
        engine.dispose()

        logger.info(
            "Final ingestion statistics: %s",
            ingestion_service.statistics(),
        )

        logger.info(
            "MotorGuard Phase 4 backend shutdown completed"
        )


if __name__ == "__main__":
    main()