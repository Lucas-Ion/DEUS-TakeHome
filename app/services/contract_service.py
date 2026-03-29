"""
contract_service.py handles all business logic for Contract operations.

Usage:
    from app.services.contract_service import create_contract, get_contract, list_contracts
"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Client, Contract
from app.schemas.schemas import ContractCreate

logger = logging.getLogger(__name__)


async def create_contract(db: AsyncSession, payload: ContractCreate) -> Contract:
    """
    Create a new shipping contract, verifying the client exists.

    Args:
        db: Active async database session.
        payload: Validated contract creation data.

    Returns:
        The newly created Contract instance.

    Raises:
        ValueError: If the referenced client does not exist.
    """
    client_result = await db.execute(select(Client).where(Client.id == payload.client_id))
    if client_result.scalar_one_or_none() is None:
        raise ValueError(f"Client id={payload.client_id} does not exist")

    logger.info(
        "Creating contract for client_id=%d destination=%s",
        payload.client_id,
        payload.destination,
    )
    contract = Contract(**payload.model_dump())
    db.add(contract)
    await db.flush()
    await db.refresh(contract)
    logger.debug("Contract created with id=%d", contract.id)
    return contract


async def get_contract(db: AsyncSession, contract_id: int) -> Contract | None:
    """
    Retrieve a single contract by primary key.

    Args:
        db: Active async database session.
        contract_id: Primary key of the contract.

    Returns:
        Contract instance or None if not found.
    """
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    return result.scalar_one_or_none()


async def list_contracts(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[Contract]:
    """
    Return a paginated list of all contracts.

    Args:
        db: Active async database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        List of Contract instances.
    """
    result = await db.execute(select(Contract).offset(skip).limit(limit))
    return list(result.scalars().all())


async def list_contracts_for_client(
    db: AsyncSession, client_id: int
) -> list[Contract]:
    """
    Return all contracts belonging to a specific cliet.

    Args:
        db: Active async database session.
        client_id: Primary key of the client.

    Returns:
        List of Contract instances for the given client.
    """
    result = await db.execute(
        select(Contract).where(Contract.client_id == client_id)
    )
    return list(result.scalars().all())
