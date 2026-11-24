
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db_session
from backend.api.services.telemetry_service import TelemetryService
from backend.api.schemas.telemetry import (
    TelemetryResponse,
    TelemetryHistoryResponse,
)


router = APIRouter(
    prefix="/api/factories/{factory_id}/motors/{motor_id}/telemetry",
    tags=["Telemetry"],
)


def build_service(
    request: Request,
    session: Session,
) -> TelemetryService:
    return TelemetryService(
        session=session,
        influx_store=request.app.state.influx_store,
    )


@router.get(
    '/latest',
    response_model=TelemetryResponse,
    summary="Get latest motor telemetry",
)
def get_latest_telemetry(
    factory_id: str,
    motor_id: str,
    request: Request,
    session: Session = Depends(get_db_session),
):
    service = build_service(request, session)

    try:
        result = service.get_latest(
            factory_id,
            motor_id,
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="No telemetry available for this motor",
            )

        return result

    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=TelemetryHistoryResponse,
    summary="Get motor telemetry history",
)
def get_telemetry_history(
    factory_id: str,
    motor_id: str,
    request: Request,
    start: datetime,
    end: datetime,
    limit: int = Query(default=500, ge=1, le=5000),
    session: Session = Depends(get_db_session),
):
    if start.tzinfo is None or start.utcoffset() is None:
        raise HTTPException(
            status_code=400,
            detail="start must contain a timezone",
        )

    if end.tzinfo is None or end.utcoffset() is None:
        raise HTTPException(
            status_code=400,
            detail="end must contain a timezone",
        )

    if start >= end:
        raise HTTPException(
            status_code=400,
            detail="start must be earlier than end",
        )

    service = build_service(request, session)

    try:
        items = service.get_history(
            factory_id,
            motor_id,
            start,
            end,
            limit,
        )

        return {
            "factory_id": factory_id,
            "motor_id": motor_id,
            "start": start,
            "end": end,
            "count": len(items),
            "limit": limit,
            "items": items,
        }

    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )
