"""
Unit tests for the clients endpoints.
"""

import pytest


@pytest.mark.asyncio
async def test_create_client_success(client):
    """Test that a client can be created successfully."""
    response = await client.post(
        "/api/v1/clients/",
        json={
            "name": "Test Corp",
            "email": "test@testcorp.com",
            "phone": "+1-800-555-0199",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Test Corp"
    assert body["email"] == "test@testcorp.com"
    assert "id" in body
    assert "created_at" in body


@pytest.mark.asyncio
async def test_create_client_duplicate_email(client, sample_client):
    """Test that creating a client with a duplicate email returns 422."""
    response = await client.post(
        "/api/v1/clients/",
        json={
            "name": "Another Corp",
            "email": sample_client["email"],
            "phone": "+1-800-555-0200",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_client_invalid_email(client):
    """Test that an invalid email address returns 422."""
    response = await client.post(
        "/api/v1/clients/",
        json={
            "name": "Test Corp",
            "email": "not-an-email",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_clients_returns_200(client):
    """Test that the list clients endpoint returns HTTP 200."""
    response = await client.get("/api/v1/clients/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_clients_returns_array(client):
    """Test that the list clients endpoint returns an array."""
    response = await client.get("/api/v1/clients/")
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_list_clients_contains_created(client, sample_client):
    """Test that a created client appears in the list."""
    response = await client.get("/api/v1/clients/")
    ids = [c["id"] for c in response.json()]
    assert sample_client["id"] in ids


@pytest.mark.asyncio
async def test_get_client_success(client, sample_client):
    """Test that an existing client can be retrieved by ID."""
    response = await client.get(f"/api/v1/clients/{sample_client['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == sample_client["id"]


@pytest.mark.asyncio
async def test_get_client_not_found(client):
    """Test that retrieving a non-existent client returns 404."""
    response = await client.get("/api/v1/clients/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_client_contracts_success(client, sample_client, sample_contract):
    """Test that a client's contracts can be listed."""
    response = await client.get(f"/api/v1/clients/{sample_client['id']}/contracts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_list_client_contracts_not_found(client):
    """Test that listing contracts for a non-existent client returns 404."""
    response = await client.get("/api/v1/clients/99999/contracts")
    assert response.status_code == 404
