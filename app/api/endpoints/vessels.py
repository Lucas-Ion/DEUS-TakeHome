"""
vessels.py defines the REST endpoints for Vessel management.

Routes:
    POST   /api/v1/vessels/              -> Register a new vessel
    GET    /api/v1/vessels/              -> List all vessels
    GET    /api/v1/vessels/{vessel_id}   -> Get a single vessel
    PATCH  /api/v1/vessels/{vessel_id}   -> Update a vessel
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.schemas import VesselCreate, VesselRead, VesselUpdate
from app.services import vessel_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/vessels", tags=["Vessels"])


@router.post("/", response_model=VesselRead, status_code=status.HTTP_201_CREATED)
async def create_vessel(
    payload: VesselCreate,
    db: AsyncSession = Depends(get_db),
) -> VesselRead:
    """
    Register a new vessel.

    Args:
        payload: Validated vessel creation data.
        db: Injected async database session.

    Returns:
        VesselRead: The newly registered vessel.

    Raises:
        HTTPException: 422 if a vessel with the same name already exists.
    """
    logger.info("POST /vessels/ name=%s", payload.name)
    try:
        vessel = await vessel_service.create_vessel(db, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    return VesselRead.model_validate(vessel)


@router.get("/", response_model=list[VesselRead])
async def list_vessels(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[VesselRead]:
    """
    Return a paginated list of all vessels.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        db: Injected async database session.

    Returns:
        list[VesselRead]: List of vessels.
    """
    vessels = await vessel_service.list_vessels(db, skip=skip, limit=limit)
    return [VesselRead.model_validate(v) for v in vessels]


@router.get("/{vessel_id}", response_model=VesselRead)
async def get_vessel(
    vessel_id: int,
    db: AsyncSession = Depends(get_db),
) -> VesselRead:
    """
    Retrieve a single vessel by ID.

    Args:
        vessel_id: Primary key of the vessel.
        db: Injected async database session.

    Returns:
        VesselRead: The requested vessel.

    Raises:
        HTTPException: 404 if vessel not found.
    """
    vessel = await vessel_service.get_vessel(db, vessel_id)
    if vessel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vessel id={vessel_id} not found",
        )
    return VesselRead.model_validate(vessel)


@router.patch("/{vessel_id}", response_model=VesselRead)
async def update_vessel(
    vessel_id: int,
    payload: VesselUpdate,
    db: AsyncSession = Depends(get_db),
) -> VesselRead:
    """
    Partially update a vessel's fields.

    Args:
        vessel_id: Primary key of the vessel to update.
        payload: Fields to update.
        db: Injected async database session.

    Returns:
        VesselRead: The updated vessel.

    Raises:
        HTTPException: 404 if vessel not found.
    """
    vessel = await vessel_service.update_vessel(db, vessel_id, payload)
    if vessel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vessel id={vessel_id} not found",
        )
    return VesselRead.model_validate(vessel)
