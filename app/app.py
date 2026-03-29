"""
app.py creates and configures the FastAPI application instance.

This file does three main things:
    - Creates the FastAPI app instance
    - Registers all routers
    - Handles startup and shutdown events
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.api.endpoints.cargoes import router as cargoes_router
from app.api.endpoints.clients import router as clients_router
from app.api.endpoints.contracts import router as contracts_router
from app.api.endpoints.health import router as health_router
from app.api.endpoints.vessels import router as vessels_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.session import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manage application startup and shutdown events.

    During Startup:
        - Initalise logging
        - Initialise the database schema

    Shutdown:
        - Logs shutdown message

    Args:
        app: takes in FastAPI application instance.
    """
    setup_logging()
    logger.info("Starting {} v{}", settings.app_name, settings.app_version)
    await init_db()
    logger.info("Application startup complete.")

    yield

    logger.info("Shutting down {}...", settings.app_name)


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application instance.
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=settings.app_description,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.include_router(health_router)
    app.include_router(clients_router, prefix=settings.api_prefix)
    app.include_router(vessels_router, prefix=settings.api_prefix)
    app.include_router(contracts_router, prefix=settings.api_prefix)
    app.include_router(cargoes_router, prefix=settings.api_prefix)

    return app


app = create_app()
