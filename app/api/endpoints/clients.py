"""
clients.py defines the REST endpoints for Client management.

Routes:
    POST   /api/v1/clients/                     -> Create a new client
    GET    /api/v1/clients/                     -> List all clients
    GET    /api/v1/clients/{client_id}          -> Get a single client
    GET    /api/v1/clients/{client_id}/contracts -> List client contracts
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.schemas import ClientCreate, ClientRead, ContractRead
from app.services import client_service, contract_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/clients", tags=["Clients"])


@router.post("/", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
async def create_client(
    payload: ClientCreate,
    db: AsyncSession = Depends(get_db),
) -> ClientRead:
    """
    Create a new client.

    Args:
        payload: Validated client creation data.
        db: Injected async database session.

    Returns:
        ClientRead: The newly created client.

    Raises:
        HTTPException: 422 if a client with the same email already exists.
    """
    logger.info("POST /clients/ name=%s", payload.name)
    try:
        client = await client_service.create_client(db, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    return ClientRead.model_validate(client)


@router.get("/", response_model=list[ClientRead])
async def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[ClientRead]:
    """
    Return a paginated list of all clients.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        db: Injected async database session.

    Returns:
        list[ClientRead]: List of clients.
    """
    clients = await client_service.list_clients(db, skip=skip, limit=limit)
    return [ClientRead.model_validate(c) for c in clients]


@router.get("/{client_id}", response_model=ClientRead)
async def get_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
) -> ClientRead:
    """
    Retrieve a single client by ID.

    Args:
        client_id: Primary key of the client.
        db: Injected async database session.

    Returns:
        ClientRead: The requested client.

    Raises:
        HTTPException: 404 if client not found.
    """
    client = await client_service.get_client(db, client_id)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client id={client_id} not found",
        )
    return ClientRead.model_validate(client)


@router.get("/{client_id}/contracts", response_model=list[ContractRead])
async def list_client_contracts(
    client_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[ContractRead]:
    """
    List all contracts for a specific client.

    Args:
        client_id: Primary key of the client.
        db: Injected async database session.

    Returns:
        list[ContractRead]: List of contracts for the client.

    Raises:
        HTTPException: 404 if client not found.
    """
    client = await client_service.get_client(db, client_id)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client id={client_id} not found",
        )
    contracts = await contract_service.list_contracts_for_client(db, client_id)
    return [ContractRead.model_validate(c) for c in contracts]
