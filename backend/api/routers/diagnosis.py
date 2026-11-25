from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db_session
from backend.api.services.diagnosis_service import DiagnosisService
from backend.api.schemas.diagnosis import DiagnosisResponse
from backend.ml.feature_extractor import FeatureExtractionError


router = APIRouter(
    prefix="/api/factories/{factory_id}/motors/{motor_id}",
    tags=["Diagnosis"],
)


def build_service(
    request: Request,
    session: Session,
) -> DiagnosisService:

    return DiagnosisService(
        session=session,
        influx_store=request.app.state.influx_store,
        model_loader=request.app.state.model_loader,
    )


@router.get(
    '/diagnosis',
    response_model=DiagnosisResponse,
    summary="Diagnose motor bearing condition",
)
def diagnose_motor(
    factory_id: str,
    motor_id: str,
    request: Request,
    session: Session = Depends(get_db_session),
):

    service = build_service(
        request=request,
        session=session,
    )

    try:

        result = service.diagnose(
            factory_id=factory_id,
            motor_id=motor_id,
        )

        return result

    except LookupError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except FeatureExtractionError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )