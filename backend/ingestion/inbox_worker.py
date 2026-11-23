import logging
import random
import threading

logger = logging.getLogger("motorguard.backend.worker")


class InboxWorker:

    def __init__(
        self,
        repository,
        influx_store,
        poll_interval=2.0,
        batch_size=100,
        max_attempts=10,
        retry_base_seconds=2,
        retry_max_seconds=300,
        processing_lease_seconds=120,
    ):

        self.repository = repository
        self.influx_store = influx_store

        self.poll_interval = poll_interval
        self.batch_size = batch_size
        self.max_attempts = max_attempts

        self.retry_base_seconds = retry_base_seconds
        self.retry_max_seconds = retry_max_seconds
        self.processing_lease_seconds = processing_lease_seconds

        self.shutdown_event = threading.Event()
        self.thread = None

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

    def _calculate_retry_delay(self, attempts):

        exponent = max(0, attempts)

        delay = self.retry_base_seconds * (2 ** exponent)

        delay = min(
            delay,
            self.retry_max_seconds,
        )

        jitter = random.uniform(0.0, delay * 0.2)

        return int(delay + jitter)

    def _run(self):

        while not self.shutdown_event.is_set():

            try:

                batch = self.repository.claim_pending_batch(
                    batch_size=self.batch_size,
                    lease_seconds=self.processing_lease_seconds,
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
                    "Inbox worker iteration failed"
                )

                self.shutdown_event.wait(
                    self.poll_interval
                )

    def _process_item(self, item):

        inbox_id = item["id"]
        payload = item["payload"]

        try:

            self.influx_store.write_telemetry(
                payload,
            )

            self.repository.mark_processed(
                inbox_id,
            )

            logger.info(
                "Telemetry processed | event=%s | motor=%s",
                item["event_key"],
                payload["motor_id"],
            )

        except Exception as exc:

            delay = self._calculate_retry_delay(
                item["attempts"],
            )

            logger.exception(
                "InfluxDB write failed | event=%s | "
                "retry_delay=%s seconds",
                item["event_key"],
                delay,
            )

            try:

                self.repository.mark_failed(
                    inbox_id=inbox_id,
                error=str(exc),
                max_attempts=self.max_attempts,
                retry_delay_seconds=delay,
            )

            except Exception:

                logger.exception(
                    "Failed to update inbox retry status | "
                    "event=%s",
                    item["event_key"],
                )

    def stop(self):

        logger.info("Stopping inbox worker")

        self.shutdown_event.set()

        if self.thread:

            self.thread.join(
                timeout=15,
            )

        logger.info("Inbox worker stopped")