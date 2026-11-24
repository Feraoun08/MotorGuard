
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import BackendConfig
from backend.database.postgres import (
    create_postgres_engine,
    create_session_factory,
)
from backend.api.routers import (
    health_router,
    factories_router,
)


logger = logging.getLogger("motorguard.api")


def get_cors_origins() -> list[str]:
    """
    Read allowed frontend origins from environment.

    Example:
        CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
    """

    raw_origins = os.getenv("CORS_ORIGINS", "")

    origins = [
        origin.strip()
        for origin in raw_origins.split(",")
        if origin.strip()
    ]

    return origins


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage API resources during application startup and shutdown.
    """

    logger.info("Starting MotorGuard API")

    config = BackendConfig.from_env()

    engine = create_postgres_engine(config)
    session_factory = create_session_factory(engine)

    app.state.config = config
    app.state.engine = engine
    app.state.session_factory = session_factory

    try:
        yield

    finally:
        logger.info("Shutting down MotorGuard API")

        engine.dispose()

        logger.info("MotorGuard API shutdown completed")


app = FastAPI(
    title="MotorGuard API",
    description=(
        "REST API for the MotorGuard predictive "
        "maintenance platform."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# CORS is enabled only when explicitly configured.
cors_origins = get_cors_origins()

if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=[
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
            "OPTIONS",
        ],
        allow_headers=["Authorization", "Content-Type"],
    )


# API routers
app.include_router(health_router)
app.include_router(factories_router)


@app.get("/", tags=["General"])
def root():
    return {
        "service": "MotorGuard API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }
