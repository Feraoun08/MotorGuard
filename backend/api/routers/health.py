
from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(
    prefix="/api/health",
    tags=["Health"],
)


@router.get("", summary="API health check")
def health_check():
    return {
        "status": "healthy",
        "service": "motorguard-api",
    }


@router.get("/ready", summary="API readiness check")
def readiness_check(request: Request):
    engine = request.app.state.engine

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ready",
            "service": "motorguard-api",
            "dependencies": {
                "postgresql": "healthy",
            },
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "service": "motorguard-api",
                "dependencies": {
                    "postgresql": "unavailable",
                },
            },
        )
