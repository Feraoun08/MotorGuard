import logging
import threading
import time

from backend.database.repositories import TelemetryRepository

logger = logging.getLogger("motorguard.backend.worker")


class InboxWorker:

    def __init__(
        self,
        repository: TelemetryRepository,
        influx_store,
        poll_interval: float = 2.0,
        batch_size: int = 100,
        max_attempts: int = 10,
    ):
        self.repository = repository
        self.influx_store = influx_store

        self.poll_interval = poll_interval
        self.batch_size = batch_size
        self.max_attempts = max_attempts

        self.shutdown_event = threading.Event()
        self.thread: threading.Thread | None = None

    def start(self):

        if self.thread and self.thread.is_alive():
            return

        self.shutdown_event.clear()

        self.thread = threading.Thread(
            target=self._run,
            name="motorguard-inbox-worker",
            daemon=True,
        )

        self.thread.start()

        logger.info("Inbox worker started")

    def _run(self):

        while not self.shutdown_event.is_set():

            try:
                batch = self.repository.get_pending_batch(
                    self.batch_size
                )

                if not batch:
                    self.shutdown_event.wait(
                        self.poll_interval
                    )
                    continue

                for item in batch:

                    if self.shutdown_event.is_set():
                        break

                    self._process_item(item)

            except Exception:
                logger.exception(
                    "Unexpected inbox worker failure"
                )

                self.shutdown_event.wait(
                    self.poll_interval
                )

    def _process_item(self, item: dict):

        inbox_id = item["id"]
        payload = item["payload"]

        try:
            self.influx_store.write_telemetry(payload)

            self.repository.mark_processed(
                inbox_id,
            )

            logger.info(
                "Inbox event processed | event=%s",
                item["event_key"],
            )

        except Exception as exc:

            logger.exception(
                "Influx persistence failed | event=%s",
                item["event_key"],
            )

            self.repository.mark_failed(
                inbox_id=inbox_id,
                error=str(exc),
                max_attempts=self.max_attempts,
            )

    def stop(self):

        logger.info("Stopping inbox worker...")

        self.shutdown_event.set()

        if self.thread:
            self.thread.join(timeout=10)

        logger.info("Inbox worker stopped")