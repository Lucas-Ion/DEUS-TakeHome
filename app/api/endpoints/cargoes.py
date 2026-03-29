"""
cargoes.py defines the REST endpoints for Cargo and Tracking management.

Routes:
    POST   /api/v1/cargoes/                          ->used to create a new cargo
    GET    /api/v1/cargoes/                          -> list all the cargoes
    GET    /api/v1/cargoes/{cargo_id}                -> get a single cargo
    GET    /api/v1/cargoes/{cargo_id}/history        -> get cargo with its full tracking history
    PATCH  /api/v1/cargoes/{cargo_id}/status         -> update the cargo status
    POST   /api/v1/cargoes/{cargo_id}/tracking       -> append a tracking event
    GET    /api/v1/cargoes/{cargo_id}/tracking       -> list all tracking events
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.schemas import (
    CargoCreate,
    CargoRead,
    CargoStatusUpdate,
    CargoWithHistory,
    TrackingEventCreate,
    TrackingEventRead,
)
from app.services import cargo_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cargoes", tags=["Cargoes & Tracking"])


@router.post("/", response_model=CargoRead, status_code=status.HTTP_201_CREATED)
async def create_cargo(
    payload: CargoCreate,
    db: AsyncSession = Depends(get_db),
) -> CargoRead:
    """
    Create a cargo entry for an existing contract.

    Args:
        payload: Validated cargo creation data.
        db: Injected async database session.

    Returns:
        CargoRead: The newly created cargo.

    Raises:
        HTTPException: 422 if contract does not exist or cargo already exists for it.
    """
    logger.info("POST /cargoes/ contract_id=%d", payload.contract_id)
    try:
        cargo = await cargo_service.create_cargo(db, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    return CargoRead.model_validate(cargo)


@router.get("/", response_model=list[CargoRead])
async def list_cargoes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[CargoRead]:
    """
    Return a paginated list of all cargoes.

    Args:
        skip: Number of records to skip.
        limit: Max number of records to return.
        db: Injected async database session.

    Returns:
        list[CargoRead]: List of cargoes.
    """
    cargoes = await cargo_service.list_cargoes(db, skip=skip, limit=limit)
    return [CargoRead.model_validate(c) for c in cargoes]


@router.get("/{cargo_id}", response_model=CargoRead)
async def get_cargo(
    cargo_id: int,
    db: AsyncSession = Depends(get_db),
) -> CargoRead:
    """
    Retrieve a single cargo by ID.

    Args:
        cargo_id: PK (Primary key) of the cargo.
        db: Injected async database session.

    Returns:
        CargoRead: The requested cargo.

    Raises:
        HTTPException: 404 if cargo not found.
    """
    cargo = await cargo_service.get_cargo(db, cargo_id)
    if cargo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cargo id={cargo_id} not found",
        )
    return CargoRead.model_validate(cargo)


@router.get("/{cargo_id}/history", response_model=CargoWithHistory)
async def get_cargo_history(
    cargo_id: int,
    db: AsyncSession = Depends(get_db),
) -> CargoWithHistory:
    """
    Retrieve a cargo with its full ordered tracking history.

    Args:
        cargo_id: PK of the cargo.
        db: Injected async database session.

    Returns:
        CargoWithHistory: The cargo with all tracking events attached.

    Raises:
        HTTPException: 404 if cargo not found.
    """
    cargo = await cargo_service.get_cargo_with_history(db, cargo_id)
    if cargo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cargo id={cargo_id} not found",
        )
    return CargoWithHistory.model_validate(cargo)


@router.patch("/{cargo_id}/status", response_model=CargoWithHistory)
async def update_cargo_status(
    cargo_id: int,
    payload: CargoStatusUpdate,
    db: AsyncSession = Depends(get_db),
) -> CargoWithHistory:
    """
    Update the cargo status and automatically append a tracking event.

    Args:
        cargo_id: PK of the cargo to update.
        payload: New status, location, and optional vessel reassignment.
        db: Injected async database session.

    Returns:
        CargoWithHistory: The updated cargo with full tracking history.

    Raises:
        HTTPException: 404 if cargo not found.
        HTTPException: 422 if referenced vessel does not exist.
    """
    logger.info("PATCH /cargoes/%d/status status=%s", cargo_id, payload.status)
    try:
        cargo = await cargo_service.update_cargo_status(db, cargo_id, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    if cargo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cargo id={cargo_id} not found",
        )
    return CargoWithHistory.model_validate(cargo)


@router.post(
    "/{cargo_id}/tracking",
    response_model=TrackingEventRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_tracking_event(
    cargo_id: int,
    payload: TrackingEventCreate,
    db: AsyncSession = Depends(get_db),
) -> TrackingEventRead:
    """
    Manualy append a tracking event for a cargo.

    Args:
        cargo_id: PK of the cargo.
        payload: Tracking event data.
        db: Injected async database session.

    Returns:
        TrackingEventRead: The newly created tracking event.

    Raises:
        HTTPException: 404 if cargo not found.
    """
    logger.info("POST /cargoes/%d/tracking location=%s", cargo_id, payload.location)
    event = await cargo_service.add_tracking_event(db, cargo_id, payload)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cargo id={cargo_id} not found",
        )
    return TrackingEventRead.model_validate(event)


@router.get("/{cargo_id}/tracking", response_model=list[TrackingEventRead])
async def list_tracking_events(
    cargo_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[TrackingEventRead]:
    """
    List all tracking events for a cargo ordered oldest first.

    Args:
        cargo_id: PK of the cargo.
        db: Injected async database session.

    Returns:
        list[TrackingEventRead]: Ordered list of tracking events.

    Raises:
        HTTPException: 404 if cargo not found.
    """
    cargo = await cargo_service.get_cargo(db, cargo_id)
    if cargo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cargo id={cargo_id} not found",
        )
    events = await cargo_service.list_tracking_events(db, cargo_id)
    return [TrackingEventRead.model_validate(e) for e in events]
