"""
test_mocked.py demonstrates  service-layer mocking using unittest.mock.

I mock the service layer directly to demonstrate isolated unit testing
of endpoint behaviour independent of any database interaction.
"""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_get_client_not_found_mocked(client):
    """
    Test 404 response when client service returns None.

    Mocks the service layer directly to verify the endpoint handles
    a missing client correctly without any database interaction.
    """
    with patch(
        "app.api.endpoints.clients.client_service.get_client",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = None
        response = await client.get("/api/v1/clients/99999")
        assert response.status_code == 404
        mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_list_clients_mocked(client):
    """
    Test list clients returns empty list when service returns none.

    Mocks the service layer to return an empty list and verifies
    the endpoint responds correctly.
    """
    with patch(
        "app.api.endpoints.clients.client_service.list_clients",
        new_callable=AsyncMock,
    ) as mock_list:
        mock_list.return_value = []
        response = await client.get("/api/v1/clients/")
        assert response.status_code == 200
        assert response.json() == []
        mock_list.assert_called_once()


@pytest.mark.asyncio
async def test_get_vessel_not_found_mocked(client):
    """
    Test 404 response when vessel service returns None.

    Mocks the service layer directly to verify the endpoint handles
    a missing vessel correctly without any database interaction.
    """
    with patch(
        "app.api.endpoints.vessels.vessel_service.get_vessel",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = None
        response = await client.get("/api/v1/vessels/99999")
        assert response.status_code == 404
        mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_get_contract_not_found_mocked(client):
    """
    Test 404 response when contract service returns None.

    Mocks the service layer directly to verify the endpoint handles
    a missing contract correctly without any database interaction.
    """
    with patch(
        "app.api.endpoints.contracts.contract_service.get_contract",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = None
        response = await client.get("/api/v1/contracts/99999")
        assert response.status_code == 404
        mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_create_contract_invalid_client_mocked(client):
    """
    Test 422 response when contract service raises ValueError.

    Mocks the service to raise a ValueError simulating a missing
    client without touching the database.
    """
    with patch(
        "app.api.endpoints.contracts.contract_service.create_contract",
        new_callable=AsyncMock,
    ) as mock_create:
        mock_create.side_effect = ValueError("Client id=99999 does not exist")
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
        assert "does not exist" in response.json()["detail"]
        mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_get_cargo_not_found_mocked(client):
    """
    Test 404 response when cargo service returns None.

    Mocks the service layer directly to verify the endpoint handles
    a missing cargo correctly without any database interaction.
    """
    with patch(
        "app.api.endpoints.cargoes.cargo_service.get_cargo",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = None
        response = await client.get("/api/v1/cargoes/99999")
        assert response.status_code == 404
        mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_update_cargo_status_invalid_vessel_mocked(client):
    """
    Test 422 response when cargo service raises ValueError for invalid vessel.

    Mocks the service to raise a ValueError simulating a missing
    vessel during a status update without touching the database.
    """
    with patch(
        "app.api.endpoints.cargoes.cargo_service.update_cargo_status",
        new_callable=AsyncMock,
    ) as mock_update:
        mock_update.side_effect = ValueError("Vessel id=99999 does not exist")
        response = await client.patch(
            "/api/v1/cargoes/1/status",
            json={
                "status": "in_transit",
                "location": "Suez Canal",
                "vessel_id": 99999,
            },
        )
        assert response.status_code == 422
        assert "does not exist" in response.json()["detail"]
        mock_update.assert_called_once()
