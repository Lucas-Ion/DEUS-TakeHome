"""
client_service.py handles all business logic for Client operations.

Usage:
    from app.services.client_service import create_client, get_client, list_clients
"""

import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Client
from app.schemas.schemas import ClientCreate

logger = logging.getLogger(__name__)


async def create_client(db: AsyncSession, payload: ClientCreate) -> Client:
    """
    Persist a new client to the database.

    Args:
        db: Active async database session.
        payload: Validated client creation data.

    Returns:
        The newly created Client instance.

    Raises:
        ValueError: If a client with the same email already exists.
    """
    logger.info("Creating client: %s (%s)", payload.name, payload.email)
    client = Client(**payload.model_dump())
    db.add(client)
    try:
        await db.flush()
        await db.refresh(client)
    except IntegrityError:
        await db.rollback()
        raise ValueError(f"Client with email {payload.email} already exists")
    logger.debug("Client created with id=%d", client.id)
    return client


async def get_client(db: AsyncSession, client_id: int) -> Client | None:
    """
    Retrieve a single client by primary key.

    Args:
        db: Active async database session.
        client_id: Primary key of the client.

    Returns:
        Client instance or None if not found.
    """
    result = await db.execute(select(Client).where(Client.id == client_id))
    return result.scalar_one_or_none()


async def list_clients(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Client]:
    """
    Return a paginated list of all clients.

    Args:
        db: Active async database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        List of Client instances.
    """
    result = await db.execute(select(Client).offset(skip).limit(limit))
    return list(result.scalars().all())
