"""
health.py is just a health check endpoint for the Logistics API.

Routes:
    GET /health -> Returns the current health status of the API.
"""

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.schemas import HealthResponse

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns the current status, version, and environment of the API.
    Used by Azure Container Apps to verify the service is running.
    Since this is a takehome I use it to demonstrate the value in a real Production app

    Returns:
        HealthResponse: The current health status of the API.
    """
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.environment,
    )
