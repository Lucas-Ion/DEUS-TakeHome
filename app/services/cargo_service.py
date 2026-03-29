"""
cargo_service.py handles all business logic for Cargo and TrackingEvent operations.

Rules which I am assuming based on the guidelines specified:
    - A contract may only have one associated cargo.
    - each status change automatically appends an TrackingEvent which is non-changeable.
    - TrackingEvents are never updated or deleted, they persist.
"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.models import Cargo, CargoStatus, Contract, TrackingEvent, Vessel
from app.schemas.schemas import CargoCreate, CargoStatusUpdate, TrackingEventCreate

logger = logging.getLogger(__name__)


async def create_cargo(db: AsyncSession, payload: CargoCreate) -> Cargo:
    """
    Create a cargo entry for an existing contract.

    Args:
        db: Active async database session.
        payload: Validated cargo creation data.

    Returns:
        The newly created Cargo instance.

    Raises:
        ValueError: If contract does not exist, cargo already exists for it,
                    or the referenced vessel does not exist.
    """
    contract_result = await db.execute(
        select(Contract).where(Contract.id == payload.contract_id)
    )
    if contract_result.scalar_one_or_none() is None:
        raise ValueError(f"Contract id={payload.contract_id} does not exist")

    existing_result = await db.execute(
        select(Cargo).where(Cargo.contract_id == payload.contract_id)
    )
    if existing_result.scalar_one_or_none() is not None:
        raise ValueError(f"Cargo already exists for contract id={payload.contract_id}")

    if payload.vessel_id is not None:
        vessel_result = await db.execute(
            select(Vessel).where(Vessel.id == payload.vessel_id)
        )
        if vessel_result.scalar_one_or_none() is None:
            raise ValueError(f"Vessel id={payload.vessel_id} does not exist")

    logger.info(
        "Creating cargo for contract_id=%d vessel_id=%s",
        payload.contract_id,
        payload.vessel_id,
    )
    cargo = Cargo(
        contract_id=payload.contract_id,
        vessel_id=payload.vessel_id,
        description=payload.description,
        weight_tons=payload.weight_tons,
        status=CargoStatus.PENDING,
    )
    db.add(cargo)
    await db.flush()
    await db.refresh(cargo)
    logger.debug("Cargo created with id=%d", cargo.id)
    return cargo


async def get_cargo(db: AsyncSession, cargo_id: int) -> Cargo | None:
    """
    Retrieve a single cargo by primary key.

    Args:
        db: Active async database session.
        cargo_id: Primary key of the cargo.

    Returns:
        Cargo instance or None if not found.
    """
    result = await db.execute(select(Cargo).where(Cargo.id == cargo_id))
    return result.scalar_one_or_none()


async def get_cargo_with_history(db: AsyncSession, cargo_id: int) -> Cargo | None:
    """
    Retrieve a cargo with its full ordered tracking history.

    Args:
        db: Active async database session.
        cargo_id: Primary key of the cargo.

    Returns:
        Cargo instance with tracking_events loaded, or None if not found.
    """
    result = await db.execute(
        select(Cargo)
        .options(selectinload(Cargo.tracking_events))
        .where(Cargo.id == cargo_id)
    )
    return result.scalar_one_or_none()


async def list_cargoes(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Cargo]:
    """
    Return a paginated list of all cargoes.

    Args:
        db: Active async database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        List of Cargo instances.
    """
    result = await db.execute(select(Cargo).offset(skip).limit(limit))
    return list(result.scalars().all())


async def update_cargo_status(
    db: AsyncSession, cargo_id: int, payload: CargoStatusUpdate
) -> Cargo | None:
    """
    Update cargo status and automatically append a TrackingEvent.

    Args:
        db: Active async database sesion.
        cargo_id: Primary key of the cargo to update.
        payload: New status, location, and optional vessel reassignment.

    Returns:
        Updated Cargo instance with tracking history loaded, or None if not found.

    Raises:
        ValueError: If the referenced vessel does not exist.
    """
    cargo = await get_cargo(db, cargo_id)
    if cargo is None:
        logger.warning("Cargo id=%d not found for status update", cargo_id)
        return None

    if payload.vessel_id is not None:
        vessel_result = await db.execute(
            select(Vessel).where(Vessel.id == payload.vessel_id)
        )
        if vessel_result.scalar_one_or_none() is None:
            raise ValueError(f"Vessel id={payload.vessel_id} does not exist")
        cargo.vessel_id = payload.vessel_id

    previous_status = cargo.status
    cargo.status = payload.status

    event = TrackingEvent(
        cargo_id=cargo_id,
        location=payload.location,
        status=payload.status,
    )
    db.add(event)
    await db.flush()

    logger.info(
        "Cargo id=%d status updated: %s -> %s at %s",
        cargo_id,
        previous_status,
        payload.status,
        payload.location,
    )
    return await get_cargo_with_history(db, cargo_id)


async def add_tracking_event(
    db: AsyncSession, cargo_id: int, payload: TrackingEventCreate
) -> TrackingEvent | None:
    """
    Manualy append a tracking event for a cargo.

    Args:
        db: Active async database session.
        cargo_id: Primary key of the cargo.
        payload: Tracking event data.

    Returns:
        The new TrackingEvent instance, or None if cargo not found.
    """
    cargo = await get_cargo(db, cargo_id)
    if cargo is None:
        return None

    cargo.status = payload.status
    event = TrackingEvent(
        cargo_id=cargo_id,
        location=payload.location,
        status=payload.status,
    )
    db.add(event)
    await db.flush()
    await db.refresh(event)
    logger.info(
        "TrackingEvent id=%d appended for cargo id=%d at %s",
        event.id,
        cargo_id,
        payload.location,
    )
    return event


async def list_tracking_events(
    db: AsyncSession, cargo_id: int
) -> list[TrackingEvent]:
    """
    Return all tracking events for a cargo ordered by recorded_at in ascending order.

    Args:
        db: Active async database session.
        cargo_id: Primary key of the cargo.

    Returns:
        List of TrackingEvent instances ordered oldest first.
    """
    result = await db.execute(
        select(TrackingEvent)
        .where(TrackingEvent.cargo_id == cargo_id)
        .order_by(TrackingEvent.recorded_at)
    )
    return list(result.scalars().all())
