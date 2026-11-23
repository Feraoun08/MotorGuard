import logging
from datetime import datetime, timezone

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

        with self.session_factory() as session:
            with session.begin():

                factory_id = payload["factory_id"]
                line_id = payload["line_id"]
                motor_id = payload["motor_id"]

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
                        "Duplicate telemetry ignored | event=%s",
                        event_key,
                    )
                    return False

                logger.info(
                    "Telemetry registered | factory=%s | "
                    "motor=%s | event=%s",
                    factory_id,
                    motor_id,
                    event_key,
                )

                return True

    def get_pending_batch(
        self,
        batch_size: int,
    ) -> list[dict]:

        with self.session_factory() as session:

            statement = (
                select(TelemetryInbox)
                .where(
                    TelemetryInbox.status == "pending"
                )
                .order_by(
                    TelemetryInbox.received_at
                )
                .limit(batch_size)
            )

            rows = session.execute(
                statement
            ).scalars().all()

            return [
                {
                    "id": row.id,
                    "event_key": row.event_key,
                    "payload": row.payload,
                    "attempts": row.attempts,
                }
                for row in rows
            ]

    def mark_processed(self, inbox_id):

        with self.session_factory() as session:
            with session.begin():

                row = session.get(
                    TelemetryInbox,
                    inbox_id,
                )

                if row is None:
                    return

                row.status = "processed"

                row.persisted_at = datetime.now(
                    timezone.utc
                )

                row.last_error = None

    def mark_failed(
        self,
        inbox_id,
        error: str,
        max_attempts: int,
    ):

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

                if row.attempts >= max_attempts:
                    row.status = "failed"
                else:
                    row.status = "pending"

    def health_check(self) -> bool:

        with self.session_factory() as session:
            session.execute(
                text("SELECT 1")
            )

        return True