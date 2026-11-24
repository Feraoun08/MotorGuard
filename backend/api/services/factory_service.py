from sqlalchemy.orm import Session

from backend.api.repositories import FactoryRepository


class FactoryService:
    """
    Business logic for factory, production-line,
    and motor API operations.
    """

    def __init__(self, session: Session):
        self.repository = FactoryRepository(session)

    
    # FACTORIES
    

    def list_factories(self):
        return self.repository.list_factories()

    def get_factory(self, factory_id: str):
        factory = self.repository.get_factory(factory_id)

        if factory is None:
            raise LookupError(
                f"Factory '{factory_id}' not found"
            )

        return factory

    
    # PRODUCTION LINES
    

    def list_lines(self, factory_id: str):
        self.get_factory(factory_id)

        return self.repository.list_lines(factory_id)

    def get_line(
        self,
        factory_id: str,
        line_id: str,
    ):
        self.get_factory(factory_id)

        line = self.repository.get_line(
            factory_id,
            line_id,
        )

        if line is None:
            raise LookupError(
                f"Production line '{line_id}' "
                f"not found in factory '{factory_id}'"
            )

        return line

    
    # MOTORS
    

    def list_motors_by_line(
        self,
        factory_id: str,
        line_id: str,
    ):
        self.get_line(factory_id, line_id)

        return self.repository.list_motors_by_line(
            factory_id,
            line_id,
        )

    def get_motor(
        self,
        factory_id: str,
        motor_id: str,
    ):
        self.get_factory(factory_id)

        motor = self.repository.get_motor(
            factory_id,
            motor_id,
        )

        if motor is None:
            raise LookupError(
                f"Motor '{motor_id}' not found "
                f"in factory '{factory_id}'"
            )

        return motor

    def list_motors(
        self,
        factory_id: str | None = None,
        line_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ):
        if factory_id is not None:
            self.get_factory(factory_id)

        if line_id is not None:
            if factory_id is None:
                raise ValueError(
                    "factory_id is required when filtering by line_id"
                )

            self.get_line(factory_id, line_id)

        items = self.repository.list_motors(
            factory_id=factory_id,
            line_id=line_id,
            limit=limit,
            offset=offset,
        )

        total = self.repository.count_motors(
            factory_id=factory_id,
            line_id=line_id,
        )

        return {
            "items": items,
            "total": total,
            "limit": limit,
            "offset": offset,
        }