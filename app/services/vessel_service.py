"""
vessel_service.py handles all busines logic for Vessel operations.

Usage:
    from app.services.vessel_service import create_vessel, get_vessel, list_vessels
"""

import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Vessel
from app.schemas.schemas import VesselCreate, VesselUpdate

logger = logging.getLogger(__name__)


async def create_vessel(db: AsyncSession, payload: VesselCreate) -> Vessel:
    """
    Register a new vessel in the db.

    Args:
        db: Active async db session.
        payload: Validated vessel creation data.

    Returns:
        The newly created Vessel instance.

    Raises:
        ValueError: If a vessel with the same name already exists.
    """
    logger.info("Registering vessel: %s", payload.name)
    vessel = Vessel(**payload.model_dump())
    db.add(vessel)
    try:
        await db.flush()
        await db.refresh(vessel)
    except IntegrityError:
        await db.rollback()
        raise ValueError(f"Vessel with name {payload.name} already exists")
    logger.debug("Vessel created with id=%d", vessel.id)
    return vessel


async def get_vessel(db: AsyncSession, vessel_id: int) -> Vessel | None:
    """
    Retrieve a single vessel by primary key.

    Args:
        db: Active async database session.
        vessel_id: Primary key of the vessel.

    Returns:
        Vessel instance or None if not found.
    """
    result = await db.execute(select(Vessel).where(Vessel.id == vessel_id))
    return result.scalar_one_or_none()


async def list_vessels(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Vessel]:
    """
    Return a paginated list of all vessels.

    Args:
        db: Active async database session.
        skip: Number of records to skip used for pagination.
        limit: Maximum number of records to return.

    Returns:
        List of Vessel instances.
    """
    result = await db.execute(select(Vessel).offset(skip).limit(limit))
    return list(result.scalars().all())


async def update_vessel(db: AsyncSession, vessel_id: int, payload: VesselUpdate) -> Vessel | None:
    """
    Partially update a vessel's mutable fields.

    Args:
        db: Active async database session.
        vessel_id: Primary key of the vessel to update.
        payload: Fields to update — None values are ignored.

    Returns:
        Updated Vessel instance or None if not found.
    """
    vessel = await get_vessel(db, vessel_id)
    if vessel is None:
        logger.warning("Vessel id=%d not found for update", vessel_id)
        return None

    update_data = payload.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(vessel, field, value)

    await db.flush()
    await db.refresh(vessel)
    logger.info("Vessel id=%d updated: %s", vessel_id, update_data)
    return vessel
