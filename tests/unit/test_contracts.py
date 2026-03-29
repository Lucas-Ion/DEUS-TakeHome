"""
test_contracts.py contains unit tests for the contracts endpoints.
"""

import pytest


@pytest.mark.asyncio
async def test_create_contract_success(client, sample_client):
    """Test that a contract can be created successfully."""
    response = await client.post(
        "/api/v1/contracts/",
        json={
            "client_id": sample_client["id"],
            "cargo_type": "Electronics",
            "destination": "Singapore",
            "price": 150000.00,
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["client_id"] == sample_client["id"]
    assert body["cargo_type"] == "Electronics"
    assert body["destination"] == "Singapore"
    assert "id" in body
    assert "created_at" in body


@pytest.mark.asyncio
async def test_create_contract_invalid_client(client):
    """Test that creating a contract with a non-existent client returns 422."""
    response = await client.post(
        "/api/v1/contracts/",
        json={
            "client_id": 99999,
            "cargo_type": "Electronics",
            "destination": "Singapore",
            "price": 150000.00,
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_contract_invalid_price(client, sample_client):
    """Test that a negative price returns 422."""
    response = await client.post(
        "/api/v1/contracts/",
        json={
            "client_id": sample_client["id"],
            "cargo_type": "Electronics",
            "destination": "Singapore",
            "price": -100.00,
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_contract_missing_fields(client, sample_client):
    """Test that missing required fields returns 422."""
    response = await client.post(
        "/api/v1/contracts/",
        json={
            "client_id": sample_client["id"],
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_contracts_returns_200(client):
    """Test that the list contracts endpoint returns HTTP 200."""
    response = await client.get("/api/v1/contracts/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_contracts_returns_array(client):
    """Test that the list contracts endpoint returns an array."""
    response = await client.get("/api/v1/contracts/")
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_list_contracts_contains_created(client, sample_contract):
    """Test that a created contract appears in the list."""
    response = await client.get("/api/v1/contracts/")
    ids = [c["id"] for c in response.json()]
    assert sample_contract["id"] in ids


@pytest.mark.asyncio
async def test_get_contract_success(client, sample_contract):
    """Test that an existing contract can be retrieved by ID."""
    response = await client.get(f"/api/v1/contracts/{sample_contract['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == sample_contract["id"]


@pytest.mark.asyncio
async def test_get_contract_not_found(client):
    """Test that retrieving a non-existent contract returns 404."""
    response = await client.get("/api/v1/contracts/99999")
    assert response.status_code == 404
