from backend.api.routers.health import router as health_router
from backend.api.routers.factories import router as factories_router
from backend.api.routers.telemetry import router as telemetry_router
from backend.api.routers.maintenance import router as maintenance_router
from backend.api.routers.diagnosis import router as diagnosis_router

__all__ = [
    "health_router",
    "factories_router",
    "telemetry_router",
    "maintenance_router",
    "diagnosis_router",
]