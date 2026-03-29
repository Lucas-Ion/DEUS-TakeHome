"""
models.py defines the ORM models for the API.

Entity relationships I assumed based of the assignment description:
    Client  has one to many for Contract
    Contract has one to one for Cargo
    Vessel  has one to many for Cargo
    Cargo has one to many TrackingEvent
"""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class CargoStatus(str, enum.Enum):
    """Lifecycle status of a cargo shipment."""

    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"


class Client(Base):
    """A client that can have shipping contracts with a company."""

    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    contracts: Mapped[list["Contract"]] = relationship(
        "Contract", back_populates="client", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Return a string representation of the Client."""
        return f"<Client id={self.id} name={self.name!r}>"


class Vessel(Base):
    """A vessel responsible for transporting cargo."""

    __tablename__ = "vessels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    capacity_tons: Mapped[float] = mapped_column(Float, nullable=False)
    current_location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    cargoes: Mapped[list["Cargo"]] = relationship("Cargo", back_populates="vessel")

    def __repr__(self) -> str:
        """Return a string representation of the Vessel."""
        return f"<Vessel id={self.id} name={self.name!r}>"


class Contract(Base):
    """A shipping contract between a client and the company."""

    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    cargo_type: Mapped[str] = mapped_column(String(255), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    client: Mapped["Client"] = relationship("Client", back_populates="contracts")
    cargo: Mapped["Cargo | None"] = relationship(
        "Cargo", back_populates="contract", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Return a string representation of the Contract."""
        return f"<Contract id={self.id} destination={self.destination!r}>"


class Cargo(Base):
    """Cargo being transported under a contract which are tied to a vessel."""

    __tablename__ = "cargoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contract_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    vessel_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("vessels.id", ondelete="SET NULL"), nullable=True
    )
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    weight_tons: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[CargoStatus] = mapped_column(
        Enum(CargoStatus), nullable=False, default=CargoStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    contract: Mapped["Contract"] = relationship("Contract", back_populates="cargo")
    vessel: Mapped["Vessel | None"] = relationship("Vessel", back_populates="cargoes")
    tracking_events: Mapped[list["TrackingEvent"]] = relationship(
        "TrackingEvent",
        back_populates="cargo",
        cascade="all, delete-orphan",
        order_by="TrackingEvent.recorded_at",
    )

    def __repr__(self) -> str:
        """Return a string representation of the Cargo."""
        return f"<Cargo id={self.id} status={self.status}>"


class TrackingEvent(Base):
    """
    A record of a cargo's location at a point in time.

    Each row represents a single movement event. The full collection
    of events for a cargo is the tracking history. Records are
    never updated or deleted, they are only appended.
    """

    __tablename__ = "tracking_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cargo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cargoes.id", ondelete="CASCADE"), nullable=False
    )
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[CargoStatus] = mapped_column(Enum(CargoStatus), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    cargo: Mapped["Cargo"] = relationship("Cargo", back_populates="tracking_events")

    def __repr__(self) -> str:
        """Return a string representation of the TrackingEvet."""
        return (
            f"<TrackingEvent id={self.id} cargo_id={self.cargo_id} "
            f"location={self.location!r} status={self.status}>"
        )
