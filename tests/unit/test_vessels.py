"""
Unit tests for the vessels endpoints.
"""

import pytest


@pytest.mark.asyncio
async def test_create_vessel_success(client):
    """Test that a vessel can be created successfully."""
    response = await client.post(
        "/api/v1/vessels/",
        json={
            "name": "MV Test Vessel",
            "capacity_tons": 15000.0,
            "current_location": "Port of Hamburg",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "MV Test Vessel"
    assert body["capacity_tons"] == 15000.0
    assert "id" in body
    assert "created_at" in body


@pytest.mark.asyncio
async def test_create_vessel_duplicate_name(client, sample_vessel):
    """Test that creating a vessel with a duplicate name returns 422."""
    response = await client.post(
        "/api/v1/vessels/",
        json={
            "name": sample_vessel["name"],
            "capacity_tons": 10000.0,
            "current_location": "Port of Hamburg",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_vessel_invalid_capacity(client):
    """Test that a negative capacity returns 422."""
    response = await client.post(
        "/api/v1/vessels/",
        json={
            "name": "MV Bad Vessel",
            "capacity_tons": -100.0,
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_vessel_missing_required_fields(client):
    """Test that missing required fields returns 422."""
    response = await client.post(
        "/api/v1/vessels/",
        json={
            "current_location": "Port of Rotterdam",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_vessels_returns_200(client):
    """Test that the list vessels endpoint returns HTTP 200."""
    response = await client.get("/api/v1/vessels/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_vessels_returns_array(client):
    """Test that the list vessels endpoint returns an array."""
    response = await client.get("/api/v1/vessels/")
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_list_vessels_contains_created(client, sample_vessel):
    """Test that a created vessel appears in the list."""
    response = await client.get("/api/v1/vessels/")
    ids = [v["id"] for v in response.json()]
    assert sample_vessel["id"] in ids


@pytest.mark.asyncio
async def test_get_vessel_success(client, sample_vessel):
    """Test that an existing vessel can be retrieved by ID."""
    response = await client.get(f"/api/v1/vessels/{sample_vessel['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == sample_vessel["id"]


@pytest.mark.asyncio
async def test_get_vessel_not_found(client):
    """Test that retrieving a non-existent vessel returns 404."""
    response = await client.get("/api/v1/vessels/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_vessel_location(client, sample_vessel):
    """Test that a vessel's location can be updated."""
    response = await client.patch(
        f"/api/v1/vessels/{sample_vessel['id']}",
        json={"current_location": "Port of Singapore"},
    )
    assert response.status_code == 200
    assert response.json()["current_location"] == "Port of Singapore"


@pytest.mark.asyncio
async def test_update_vessel_not_found(client):
    """Test that updating a non-existent vessel returns 404."""
    response = await client.patch(
        "/api/v1/vessels/99999",
        json={"current_location": "Port of Singapore"},
    )
    assert response.status_code == 404
