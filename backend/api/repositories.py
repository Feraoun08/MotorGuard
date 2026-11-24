
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.database.models import Factory, ProductionLine, Motor


class FactoryRepository:
    """
    Read operations for factories, production lines and motors.

    This repository is used exclusively by the REST API.
    It does not modify the Phase 4 ingestion repository.
    """

    def __init__(self, session: Session):
        self.session = session

    
    # FACTORIES
    

    def list_factories(self) -> list[Factory]:
        statement = (
            select(Factory)
            .order_by(Factory.id)
        )

        return list(self.session.scalars(statement).all())

    def get_factory(self, factory_id: str) -> Factory | None:
        statement = select(Factory).where(
            Factory.id == factory_id
        )

        return self.session.scalar(statement)

    def count_factories(self) -> int:
        statement = select(func.count()).select_from(Factory)

        return self.session.scalar(statement) or 0

    
    # PRODUCTION LINES
    

    def list_lines(
        self,
        factory_id: str,
    ) -> list[ProductionLine]:
        statement = (
            select(ProductionLine)
            .where(
                ProductionLine.factory_id == factory_id
            )
            .order_by(ProductionLine.id)
        )

        return list(self.session.scalars(statement).all())

    def get_line(
        self,
        factory_id: str,
        line_id: str,
    ) -> ProductionLine | None:
        statement = select(ProductionLine).where(
            ProductionLine.factory_id == factory_id,
            ProductionLine.id == line_id,
        )

        return self.session.scalar(statement)

    def count_lines(
        self,
        factory_id: str,
    ) -> int:
        statement = (
            select(func.count())
            .select_from(ProductionLine)
            .where(
                ProductionLine.factory_id == factory_id
            )
        )

        return self.session.scalar(statement) or 0

    
    # MOTORS
    

    def list_motors_by_line(
        self,
        factory_id: str,
        line_id: str,
    ) -> list[Motor]:
        statement = (
            select(Motor)
            .where(
                Motor.factory_id == factory_id,
                Motor.line_id == line_id,
            )
            .order_by(Motor.id)
        )

        return list(self.session.scalars(statement).all())

    def get_motor(
        self,
        factory_id: str,
        motor_id: str,
    ) -> Motor | None:
        statement = select(Motor).where(
            Motor.factory_id == factory_id,
            Motor.id == motor_id,
        )

        return self.session.scalar(statement)

    def list_motors(
        self,
        factory_id: str | None = None,
        line_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Motor]:
        statement = select(Motor)

        if factory_id is not None:
            statement = statement.where(
                Motor.factory_id == factory_id
            )

        if line_id is not None:
            statement = statement.where(
                Motor.line_id == line_id
            )

        statement = (
            statement
            .order_by(Motor.factory_id, Motor.id)
            .limit(limit)
            .offset(offset)
        )

        return list(self.session.scalars(statement).all())

    def count_motors(
        self,
        factory_id: str | None = None,
        line_id: str | None = None,
    ) -> int:
        statement = select(func.count()).select_from(Motor)

        if factory_id is not None:
            statement = statement.where(
                Motor.factory_id == factory_id
            )

        if line_id is not None:
            statement = statement.where(
                Motor.line_id == line_id
            )

        return self.session.scalar(statement) or 0
