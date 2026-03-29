"""
dependencies.py is used to define the shared FastAPI dependencies.

In this file I define reusable Depends() functions that can be injected into any endpoint.
"""

import logging

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.models import Cargo, Client, Contract, Vessel
from app.services import cargo_service, client_service, contract_service, vessel_service

logger = logging.getLogger(__name__)


async def get_client_or_404(
    client_id: int,
    db: AsyncSession = Depends(get_db),
) -> Client:
    """
    Retrieve a client by ID or raise a 404 HTTP exception.

    Args:
        client_id: Primary key of the client.
        db: Injected async database session.

    Returns:
        Client: The requested client instance.

    Raises:
        HTTPException: 404 if client not found.
    """
    client = await client_service.get_client(db, client_id)
    if client is None:
        logger.warning("Client id=%d not found", client_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client id={client_id} not found",
        )
    return client


async def get_vessel_or_404(
    vessel_id: int,
    db: AsyncSession = Depends(get_db),
) -> Vessel:
    """
    Retrieve a vessel by ID or raise a 404 HTTP exception

    Args:
        vessel_id: Primary key of the vessel.
        db: Injected async database session.

    Returns:
        Vessel: The requested vessel instance.

    Raises:
        HTTPException: 404 if vessel not found.
    """
    vessel = await vessel_service.get_vessel(db, vessel_id)
    if vessel is None:
        logger.warning("Vessel id=%d not found", vessel_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vessel id={vessel_id} not found",
        )
    return vessel


async def get_contract_or_404(
    contract_id: int,
    db: AsyncSession = Depends(get_db),
) -> Contract:
    """
    Retrieve a contract by ID or raise a 404 HTTP exception.

    Args:
        contract_id: Primary key of the contract.
        db: Injected async database session.

    Returns:
        Contract: The requested contract instance.

    Raises:
        HTTPException: 404 if contract not found.
    """
    contract = await contract_service.get_contract(db, contract_id)
    if contract is None:
        logger.warning("Contract id=%d not found", contract_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract id={contract_id} not found",
        )
    return contract


async def get_cargo_or_404(
    cargo_id: int,
    db: AsyncSession = Depends(get_db),
) -> Cargo:
    """
    Retrieve a cargo by ID or raise a 404 HTTP exception.

    Args:
        cargo_id: Primary key of the cargo.
        db: Injected async database session.

    Returns:
        Cargo: The requested cargo instance.

    Raises:
        HTTPException: 404 if cargo not found.
    """
    cargo = await cargo_service.get_cargo(db, cargo_id)
    if cargo is None:
        logger.warning("Cargo id=%d not found", cargo_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cargo id={cargo_id} not found",
        )
    return cargo
