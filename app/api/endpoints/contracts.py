"""
contracts.py defines the REST endpoints for Contract management.

Routes:
    POST   /api/v1/contracts/                -> Create a new contract
    GET    /api/v1/contracts/                ->List all contracts
    GET    /api/v1/contracts/{contract_id}   -> Get a single contractt
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.schemas import ContractCreate, ContractRead
from app.services import contract_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/contracts", tags=["Contracts"])


@router.post("/", response_model=ContractRead, status_code=status.HTTP_201_CREATED)
async def create_contract(
    payload: ContractCreate,
    db: AsyncSession = Depends(get_db),
) -> ContractRead:
    """
    Create a new shipping contract.

    Args:
        payload: Validated contract creation data.
        db: Injected async database session.

    Returns:
        ContractRead: The newly created contract.

    Raises:
        HTTPException: 422 if the referenced client does not exist.
    """
    logger.info("POST /contracts/ client_id=%d", payload.client_id)
    try:
        contract = await contract_service.create_contract(db, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    return ContractRead.model_validate(contract)


@router.get("/", response_model=list[ContractRead])
async def list_contracts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[ContractRead]:
    """
    Return a paginated list of all contracts.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        db: Injected async database session.

    Returns:
        list[ContractRead]: List of contracts.
    """
    contracts = await contract_service.list_contracts(db, skip=skip, limit=limit)
    return [ContractRead.model_validate(c) for c in contracts]


@router.get("/{contract_id}", response_model=ContractRead)
async def get_contract(
    contract_id: int,
    db: AsyncSession = Depends(get_db),
) -> ContractRead:
    """
    Retrieve a single contract by ID.

    Args:
        contract_id: PK of the contract.
        db: Injected async database session.

    Returns:
        ContractRead: The requested contract.

    Raises:
        HTTPException: 404 if contract not found.
    """
    contract = await contract_service.get_contract(db, contract_id)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract id={contract_id} not found",
        )
    return ContractRead.model_validate(contract)
