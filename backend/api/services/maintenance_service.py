from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models import Motor, MaintenanceRecord
from backend.api.schemas.maintenance import MaintenanceCreate


class MaintenanceService:

    def __init__(self, session: Session):
        self.session = session

    def get_motor(
        self,
        factory_id: str,
        motor_id: str,
    ):
        statement = select(Motor).where(
            Motor.factory_id == factory_id,
            Motor.id == motor_id,
        )

        motor = self.session.execute(statement).scalar_one_or_none()

        if motor is None:
            return None

        return motor

    def get_maintenance_history(
        self,
        factory_id: str,
        motor_id: str,
    ):
        motor = self.get_motor(factory_id, motor_id)

        if motor is None:
            return None

        statement = (
            select(MaintenanceRecord)
            .where(
                MaintenanceRecord.factory_id == factory_id,
                MaintenanceRecord.motor_id == motor_id,
            )
            .order_by(MaintenanceRecord.performed_at.desc())
        )

        return self.session.execute(statement).scalars().all()

    def create_maintenance(
        self,
        factory_id: str,
        motor_id: str,
        payload: MaintenanceCreate,
    ):
        motor = self.get_motor(factory_id, motor_id)

        if motor is None:
            return None

        record = MaintenanceRecord(
            factory_id=factory_id,
            motor_id=motor_id,
            maintenance_type=payload.maintenance_type,
            description=payload.description,
            performed_at=payload.performed_at,
        )

        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)

        return record