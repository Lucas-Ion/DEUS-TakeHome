"""
test_cargoes.py contains unit tests for the cargoes and tracking endpoints.
"""

import pytest


@pytest.mark.asyncio
async def test_create_cargo_success(client, sample_contract, sample_vessel):
    """Test that a cargo can be created successfully."""
    response = await client.post(
        "/api/v1/cargoes/",
        json={
            "contract_id": sample_contract["id"],
            "vessel_id": sample_vessel["id"],
            "description": "500 units of LCD panels",
            "weight_tons": 12.5,
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["contract_id"] == sample_contract["id"]
    assert body["vessel_id"] == sample_vessel["id"]
    assert body["status"] == "pending"
    assert "id" in body


@pytest.mark.asyncio
async def test_create_cargo_duplicate_contract(
    client, sample_cargo, sample_vessel, sample_contract
):
    """Test that creating a second cargo for the same contract returns 422."""
    response = await client.post(
        "/api/v1/cargoes/",
        json={
            "contract_id": sample_contract["id"],
            "vessel_id": sample_vessel["id"],
            "description": "Duplicate cargo",
            "weight_tons": 5.0,
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_cargo_invalid_contract(client, sample_vessel):
    """Test that creating cargo with a non-existent contract returns 422."""
    response = await client.post(
        "/api/v1/cargoes/",
        json={
            "contract_id": 99999,
            "vessel_id": sample_vessel["id"],
            "description": "Some cargo",
            "weight_tons": 5.0,
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_cargo_invalid_vessel(client, sample_contract):
    """Test that creating cargo with a non-existent vessel returns 422."""
    response = await client.post(
        "/api/v1/cargoes/",
        json={
            "contract_id": sample_contract["id"],
            "vessel_id": 99999,
            "description": "Some cargo",
            "weight_tons": 5.0,
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_cargo_invalid_weight(client, sample_contract, sample_vessel):
    """Test that a negative weight returns 422."""
    response = await client.post(
        "/api/v1/cargoes/",
        json={
            "contract_id": sample_contract["id"],
            "vessel_id": sample_vessel["id"],
            "description": "Some cargo",
            "weight_tons": -10.0,
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_cargoes_returns_200(client):
    """Test that the list cargoes endpoint returns HTTP 200."""
    response = await client.get("/api/v1/cargoes/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_cargoes_returns_array(client):
    """Test that the list cargoes endpoint returns an array."""
    response = await client.get("/api/v1/cargoes/")
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_list_cargoes_contains_created(client, sample_cargo):
    """Test that a created cargo appears in the list."""
    response = await client.get("/api/v1/cargoes/")
    ids = [c["id"] for c in response.json()]
    assert sample_cargo["id"] in ids


@pytest.mark.asyncio
async def test_get_cargo_success(client, sample_cargo):
    """Test that an existing cargo can be retrieved by ID."""
    response = await client.get(f"/api/v1/cargoes/{sample_cargo['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == sample_cargo["id"]


@pytest.mark.asyncio
async def test_get_cargo_not_found(client):
    """Test that retrieving a non-existent cargo returns 404."""
    response = await client.get("/api/v1/cargoes/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_cargo_status_in_transit(client, sample_cargo):
    """Test that cargo status can be updated to in_transit."""
    response = await client.patch(
        f"/api/v1/cargoes/{sample_cargo['id']}/status",
        json={
            "status": "in_transit",
            "location": "Suez Canal",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "in_transit"
    assert len(body["tracking_events"]) == 1
    assert body["tracking_events"][0]["location"] == "Suez Canal"


@pytest.mark.asyncio
async def test_update_cargo_status_delivered(client, sample_cargo):
    """Test that cargo status can be updated to delivered."""
    response = await client.patch(
        f"/api/v1/cargoes/{sample_cargo['id']}/status",
        json={
            "status": "delivered",
            "location": "Port of Singapore",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "delivered"


@pytest.mark.asyncio
async def test_update_cargo_status_appends_tracking_events(client, sample_cargo):
    """Test that multiple status updates each append a tracking event."""
    await client.patch(
        f"/api/v1/cargoes/{sample_cargo['id']}/status",
        json={"status": "in_transit", "location": "Suez Canal"},
    )
    await client.patch(
        f"/api/v1/cargoes/{sample_cargo['id']}/status",
        json={"status": "delivered", "location": "Port of Singapore"},
    )
    response = await client.get(f"/api/v1/cargoes/{sample_cargo['id']}/history")
    assert len(response.json()["tracking_events"]) == 2


@pytest.mark.asyncio
async def test_update_cargo_status_not_found(client):
    """Test that updating a non-existent cargo status returns 404."""
    response = await client.patch(
        "/api/v1/cargoes/99999/status",
        json={"status": "in_transit", "location": "Suez Canal"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_cargo_history_success(client, sample_cargo):
    """Test that cargo history is returned with tracking events."""
    await client.patch(
        f"/api/v1/cargoes/{sample_cargo['id']}/status",
        json={"status": "in_transit", "location": "Suez Canal"},
    )
    response = await client.get(f"/api/v1/cargoes/{sample_cargo['id']}/history")
    assert response.status_code == 200
    body = response.json()
    assert "tracking_events" in body
    assert isinstance(body["tracking_events"], list)


@pytest.mark.asyncio
async def test_get_cargo_history_not_found(client):
    """Test that getting history for a non-existent cargo returns 404."""
    response = await client.get("/api/v1/cargoes/99999/history")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_add_tracking_event_success(client, sample_cargo):
    """Test that a tracking event can be manually appended."""
    response = await client.post(
        f"/api/v1/cargoes/{sample_cargo['id']}/tracking",
        json={
            "location": "Port of Hamburg",
            "status": "in_transit",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["location"] == "Port of Hamburg"
    assert body["status"] == "in_transit"
    assert body["cargo_id"] == sample_cargo["id"]


@pytest.mark.asyncio
async def test_add_tracking_event_not_found(client):
    """Test that adding a tracking event to a non-existent cargo returns 404."""
    response = await client.post(
        "/api/v1/cargoes/99999/tracking",
        json={
            "location": "Port of Hamburg",
            "status": "in_transit",
        },
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_tracking_events_success(client, sample_cargo):
    """Test that tracking events can be listed for a cargo."""
    await client.post(
        f"/api/v1/cargoes/{sample_cargo['id']}/tracking",
        json={"location": "Port of Hamburg", "status": "in_transit"},
    )
    response = await client.get(f"/api/v1/cargoes/{sample_cargo['id']}/tracking")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_list_tracking_events_not_found(client):
    """Test that listing tracking events for a non-existent cargo returns 404."""
    response = await client.get("/api/v1/cargoes/99999/tracking")
    assert response.status_code == 404
