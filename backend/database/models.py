import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    Text,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


def utc_now():
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Factory(Base):
    __tablename__ = "factories"

    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    lines: Mapped[list["ProductionLine"]] = relationship(
        back_populates="factory",
        cascade="all, delete-orphan",
    )


class ProductionLine(Base):
    __tablename__ = "production_lines"

    factory_id: Mapped[str] = mapped_column(
        ForeignKey("factories.id", ondelete="CASCADE"),
        primary_key=True,
    )

    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    factory: Mapped["Factory"] = relationship(
        back_populates="lines",
    )

    motors: Mapped[list["Motor"]] = relationship(
        back_populates="line",
    )


class Motor(Base):
    __tablename__ = "motors"

    factory_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    line_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["factory_id", "line_id"],
            [
                "production_lines.factory_id",
                "production_lines.id",
            ],
            ondelete="RESTRICT",
        ),
    )

    line: Mapped["ProductionLine"] = relationship(
        back_populates="motors",
    )

    maintenance_records: Mapped[list["MaintenanceRecord"]] = (
        relationship(
            back_populates="motor",
            cascade="all, delete-orphan",
        )
    )


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    factory_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    motor_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    maintenance_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    performed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["factory_id", "motor_id"],
            ["motors.factory_id", "motors.id"],
            ondelete="CASCADE",
        ),
    )

    motor: Mapped["Motor"] = relationship(
        back_populates="maintenance_records",
    )


class TelemetryInbox(Base):
    __tablename__ = "telemetry_inbox"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    event_key: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )

    topic: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    factory_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    motor_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    line_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
        index=True,
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    persisted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        Index(
            "ix_inbox_status_received",
            "status",
            "received_at",
        ),
    )