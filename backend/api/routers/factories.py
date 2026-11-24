
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db_session
from backend.api.services.factory_service import FactoryService
from backend.api.schemas.factory import (
    FactoryResponse,
    ProductionLineResponse,
    MotorResponse,
    MotorListResponse,
)


router = APIRouter(
    prefix="/api",
    tags=["Factories & Motors"],
)


def get_factory_service(
    session: Session = Depends(get_db_session),
) -> FactoryService:
    return FactoryService(session)


# =============================================================
# FACTORIES
# =============================================================

@router.get(
    '/factories',
    response_model=list[FactoryResponse],
    summary="List factories",
)
def list_factories(
    service: FactoryService = Depends(get_factory_service),
):
    return service.list_factories()


@router.get(
    "/factories/{factory_id}",
    response_model=FactoryResponse,
    summary="Get factory details",
)
def get_factory(
    factory_id: str,
    service: FactoryService = Depends(get_factory_service),
):
    try:
        return service.get_factory(factory_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# =============================================================
# PRODUCTION LINES
# =============================================================

@router.get(
    '/factories/{factory_id}/lines',
    response_model=list[ProductionLineResponse],
    summary="List production lines",
)
def list_production_lines(
    factory_id: str,
    service: FactoryService = Depends(get_factory_service),
):
    try:
        return service.list_lines(factory_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get(
    '/factories/{factory_id}/lines/{line_id}',
    response_model=ProductionLineResponse,
    summary="Get production line details",
)
def get_production_line(
    factory_id: str,
    line_id: str,
    service: FactoryService = Depends(get_factory_service),
):
    try:
        return service.get_line(factory_id, line_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# =============================================================
# MOTORS BY LINE
# =============================================================

@router.get(
    '/factories/{factory_id}/lines/{line_id}/motors',
    response_model=list[MotorResponse],
    summary="List motors belonging to a production line",
)
def list_line_motors(
    factory_id: str,
    line_id: str,
    service: FactoryService = Depends(get_factory_service),
):
    try:
        return service.list_motors_by_line(factory_id, line_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# =============================================================
# MOTOR DETAILS
# =============================================================

@router.get(
    '/factories/{factory_id}/motors/{motor_id}',
    response_model=MotorResponse,
    summary="Get motor details",
)
def get_motor(
    factory_id: str,
    motor_id: str,
    service: FactoryService = Depends(get_factory_service),
):
    try:
        return service.get_motor(factory_id, motor_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# =============================================================
# MOTOR LIST
# =============================================================

@router.get(
    '/motors',
    response_model=MotorListResponse,
    summary="List and filter motors",
)
def list_motors(
    factory_id: str | None = None,
    line_id: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    service: FactoryService = Depends(get_factory_service),
):
    try:
        return service.list_motors(
            factory_id=factory_id,
            line_id=line_id,
            limit=limit,
            offset=offset,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
