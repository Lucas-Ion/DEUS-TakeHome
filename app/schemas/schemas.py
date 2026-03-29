"""
schemas.py defines the Pydantic schemas for the API.

Usage:
    from app.schemas.schemas import ClientCreate, ClientRead
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, PositiveFloat

from app.models.models import CargoStatus


class HealthResponse(BaseModel):
    """Schema for the health check response."""

    status: str
    version: str
    environment: str


class ClientBase(BaseModel):
    """Shared fields for Client schemas."""

    name: str = Field(..., max_length=255, examples=["DEUS Shipping Company LLC"])
    email: EmailStr = Field(..., examples=["contact@deus.com"])
    phone: str | None = Field(None, max_length=50, examples=["+351-123-456-7890"])


class ClientCreate(ClientBase):
    """Payload for creating a new client."""


class ClientRead(ClientBase):
    """Client represntation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class VesselBase(BaseModel):
    """Shared fields for Vessel schemas."""

    name: str = Field(..., max_length=255, examples=["Atlantic Star Vessels"])
    capacity_tons: PositiveFloat = Field(..., examples=[25000.0])
    current_location: str | None = Field(
        None, max_length=255, examples=["Port of Rotterdam"]
    )


class VesselCreate(VesselBase):
    """Payload for registering a new vessel."""


class VesselRead(VesselBase):
    """Vessel representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class VesselUpdate(BaseModel):
    """Partial update payload for a vessel."""

    current_location: str | None = Field(None, max_length=255)
    capacity_tons: PositiveFloat | None = None


class ContractBase(BaseModel):
    """Shared fields for Contract schemas."""

    cargo_type: str = Field(..., max_length=255, examples=["Electronics"])
    destination: str = Field(..., max_length=255, examples=["Singapore"])
    price: Decimal = Field(..., gt=0, decimal_places=2, examples=["150000.00"])


class ContractCreate(ContractBase):
    """Payload for creating a new contract."""

    client_id: int = Field(..., examples=[1])


class ContractRead(ContractBase):
    """Contract representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    created_at: datetime


class CargoBase(BaseModel):
    """Shared fields for Cargo schemas."""

    description: str = Field(..., max_length=500, examples=["500 units of LCD panels"])
    weight_tons: PositiveFloat = Field(..., examples=[12.5])


class CargoCreate(CargoBase):
    """Payload for creating a new cargo entry."""

    contract_id: int = Field(..., examples=[1])
    vessel_id: int | None = Field(None, examples=[2])


class CargoStatusUpdate(BaseModel):
    """Payload for updating cargo status and recording a tracking event."""

    status: CargoStatus
    location: str = Field(..., max_length=255, examples=["Suez Canal"])
    vessel_id: int | None = Field(None, examples=[1])


class CargoRead(CargoBase):
    """Cargo representation that is returnd by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    contract_id: int
    vessel_id: int | None
    status: CargoStatus
    created_at: datetime
    updated_at: datetime


class TrackingEventCreate(BaseModel):
    """Payload for manually appending a tracking event."""

    location: str = Field(..., max_length=255, examples=["Port of Leixões"])
    status: CargoStatus


class TrackingEventRead(BaseModel):
    """Tracking event representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    cargo_id: int
    location: str
    status: CargoStatus
    recorded_at: datetime


class CargoWithHistory(CargoRead):
    """Cargo with its full ordered tracking history."""

    tracking_events: list[TrackingEventRead] = []
