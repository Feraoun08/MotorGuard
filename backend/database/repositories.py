import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert

from backend.database.models import (
    Factory,
    ProductionLine,
    Motor,
    TelemetryInbox,
)

logger = logging.getLogger("motorguard.backend.repository")


class TelemetryRepository:

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def register_telemetry(
        self,
        event_key: str,
        topic: str,
        payload: dict,
    ) -> bool:

        factory_id = payload["factory_id"]
        line_id = payload["line_id"]
        motor_id = payload["motor_id"]

        with self.session_factory() as session:
            with session.begin():

                session.execute(
                    insert(Factory)
                    .values(
                        id=factory_id,
                        name=factory_id,
                    )
                    .on_conflict_do_nothing(
                        index_elements=["id"]
                    )
                )

                session.execute(
                    insert(ProductionLine)
                    .values(
                        factory_id=factory_id,
                        id=line_id,
                        name=line_id,
                    )
                    .on_conflict_do_nothing(
                        index_elements=["factory_id", "id"]
                    )
                )

                session.execute(
                    insert(Motor)
                    .values(
                        factory_id=factory_id,
                        id=motor_id,
                        line_id=line_id,
                        name=payload["motor_name"],
                    )
                    .on_conflict_do_nothing(
                        index_elements=["factory_id", "id"]
                    )
                )

                statement = (
                    insert(TelemetryInbox)
                    .values(
                        event_key=event_key,
                        topic=topic,
                        factory_id=factory_id,
                        motor_id=motor_id,
                        line_id=line_id,
                        payload=payload,
                        status="pending",
                        attempts=0,
                        next_attempt_at=datetime.now(timezone.utc),
                    )
                    .on_conflict_do_nothing(
                        index_elements=["event_key"]
                    )
                    .returning(TelemetryInbox.id)
                )

                inserted_id = session.execute(
                    statement
                ).scalar_one_or_none()

                if inserted_id is None:
                    logger.info(
                        "Duplicate event ignored | event=%s",
                        event_key,
                    )
                    return False

                return True

    def claim_pending_batch(
        self,
        batch_size: int,
        lease_seconds: int,
    ) -> list[dict]:

        now = datetime.now(timezone.utc)
        expired_before = now - timedelta(seconds=lease_seconds)

        with self.session_factory() as session:
            with session.begin():

                # Recover events whose worker died while
                # processing them.
                session.execute(
                    text(
                        """
                        UPDATE telemetry_inbox
                        SET status = 'pending',
                            processing_started_at = NULL
                        WHERE status = 'processing'
                          AND processing_started_at < :expired_before
                        """
                    ),
                    {
                        "expired_before": expired_before,
                    },
                )

                statement = (
                    select(TelemetryInbox)
                    .where(
                        TelemetryInbox.status == "pending",
                        TelemetryInbox.next_attempt_at <= now,
                    )
                    .order_by(
                        TelemetryInbox.received_at,
                    )
                    .limit(batch_size)
                    .with_for_update(skip_locked=True)
                )

                rows = session.execute(
                    statement
                ).scalars().all()

                claimed = []

                for row in rows:

                    row.status = "processing"
                    row.processing_started_at = now

                    claimed.append(
                        {
                            "id": row.id,
                            "event_key": row.event_key,
                            "payload": row.payload,
                            "attempts": row.attempts,
                        }
                    )

                return claimed

    def mark_processed(self, inbox_id):

        now = datetime.now(timezone.utc)

        with self.session_factory() as session:
            with session.begin():

                row = session.get(
                    TelemetryInbox,
                    inbox_id,
                )

                if row is None:
                    return

                row.status = "processed"
                row.persisted_at = now
                row.processed_at = now
                row.processing_started_at = None
                row.last_error = None

    def mark_failed(
        self,
        inbox_id,
        error: str,
        max_attempts: int,
        retry_delay_seconds: int,
    ):

        now = datetime.now(timezone.utc)

        with self.session_factory() as session:
            with session.begin():

                row = session.get(
                    TelemetryInbox,
                    inbox_id,
                )

                if row is None:
                    return

                row.attempts += 1
                row.last_error = error[:5000]
                row.processing_started_at = None

                if row.attempts >= max_attempts:

                    row.status = "failed"

                    logger.error(
                        "Event reached maximum retries | "
                        "event=%s | attempts=%s",
                        row.event_key,
                        row.attempts,
                    )

                else:

                    row.status = "pending"
                    row.next_attempt_at = (
                        now + timedelta(
                            seconds=retry_delay_seconds
                        )
                    )

    def health_check(self) -> bool:

        with self.session_factory() as session:
            session.execute(
                text("SELECT 1")
            )

        return True