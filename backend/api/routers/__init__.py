from backend.api.routers.health import router as health_router
from backend.api.routers.factories import router as factories_router

__all__ = [
    "health_router",
    "factories_router",
]