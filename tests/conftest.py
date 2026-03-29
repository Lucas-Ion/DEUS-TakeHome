"""
conftest.py defines the pytest fixtures for the test suite.
"""

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.app import create_app
from app.db.session import Base, get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_engine():
    """
    Creates a new in-memory SQLite engine for each test.
    """
    engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    """
    Provide a new async database session for each test.
    """
    test_session_local = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    async with test_session_local() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    """
    Provide an async HTTP test client with the test database injected.

    Overrides the get_db dependency to use the test session so all
    requests hit the in-memory database instead of the real one.

    Args:
        db_session: The test-scoped database session fixture.

    Yields:
        AsyncClient: An httpx async client bound to the FastAPI app.
    """
    app = create_app()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def sample_client(client):
    """
    Create and return a sample client via the API.

    Args:
        client: The async HTTP test client fixture.

    Returns:
        dict: The created client response body.
    """
    response = await client.post(
        "/api/v1/clients/",
        json={
            "name": "DEUS Shipping Corp",
            "email": "contact@deusshipping.com",
            "phone": "+351-123-456-789",
        },
    )
    return response.json()


@pytest_asyncio.fixture
async def sample_vessel(client):
    """
    Create and return a sample vessel via the API.

    Args:
        client: The async HTTP test client fixture.

    Returns:
        dict: The created vessel response body.
    """
    response = await client.post(
        "/api/v1/vessels/",
        json={
            "name": "Atlantic Star",
            "capacity_tons": 25000.0,
            "current_location": "Port of Port of Leixões",
        },
    )
    return response.json()


@pytest_asyncio.fixture
async def sample_contract(client, sample_client):
    """
    Create and return a sample contract via the API.

    Args:
        client: The async HTTP test client fixture.
        sample_client: The sample client fixture.

    Returns:
        dict: The created contract response body.
    """
    response = await client.post(
        "/api/v1/contracts/",
        json={
            "client_id": sample_client["id"],
            "cargo_type": "Electronics",
            "destination": "Singapore",
            "price": 150000.00,
        },
    )
    return response.json()


@pytest_asyncio.fixture
async def sample_cargo(client, sample_contract, sample_vessel):
    """
    Create and return a sample cargo via the API.

    Args:
        client: The async HTTP test client fixture.
        sample_contract: The sample contract fixture.
        sample_vessel: The sample vessel fixture.

    Returns:
        dict: The created cargo response body.
    """
    response = await client.post(
        "/api/v1/cargoes/",
        json={
            "contract_id": sample_contract["id"],
            "vessel_id": sample_vessel["id"],
            "description": "500 units of LCD panels",
            "weight_tons": 12.5,
        },
    )
    return response.json()
