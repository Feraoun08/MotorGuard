from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db_session
from backend.api.services.maintenance_service import MaintenanceService
from backend.api.schemas.maintenance import (
    MaintenanceCreate,
    MaintenanceResponse,
)


router = APIRouter(
    prefix="/api/factories/{factory_id}/motors/{motor_id}/maintenance",
    tags=["Maintenance"],
)


@router.get(
    "",
    response_model=list[MaintenanceResponse],
)
def get_maintenance_history(
    factory_id: str,
    motor_id: str,
    session: Session = Depends(get_db_session),
):
    service = MaintenanceService(session)

    records = service.get_maintenance_history(
        factory_id=factory_id,
        motor_id=motor_id,
    )

    if records is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Motor not found",
        )

    return records


@router.post(
    "",
    response_model=MaintenanceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_maintenance_record(
    factory_id: str,
    motor_id: str,
    payload: MaintenanceCreate,
    session: Session = Depends(get_db_session),
):
    service = MaintenanceService(session)

    record = service.create_maintenance(
        factory_id=factory_id,
        motor_id=motor_id,
        payload=payload,
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Motor not found",
        )

    return record