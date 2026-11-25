
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from backend.api.app import app
from backend.api.dependencies import get_db_session
import backend.api.routers.telemetry as telemetry_router


@pytest.fixture
def telemetry_service():
    return Mock()


@pytest.fixture
def client(monkeypatch, telemetry_service):
    # Replace the service factory to isolate the router from
    # PostgreSQL and InfluxDB.
    monkeypatch.setattr(
        telemetry_router,
        "build_service",
        lambda request, session: telemetry_service,
    )

    # Provide a mock database session.
    app.dependency_overrides[get_db_session] = lambda: Mock()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ---------------------------------------------------------
# LATEST TELEMETRY ROUTER
# ---------------------------------------------------------


def test_latest_returns_404_when_no_telemetry(
    client,
    telemetry_service,
):
    telemetry_service.get_latest.return_value = None

    response = client.get(
        "/api/factories/factory-01/motors/motor-01/telemetry/latest"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "No telemetry available for this motor"
    )


def test_latest_returns_404_for_unknown_motor(
    client,
    telemetry_service,
):
    telemetry_service.get_latest.side_effect = LookupError(
        "Motor not found"
    )

    response = client.get(
        "/api/factories/factory-01/motors/motor-999/telemetry/latest"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Motor not found"


# ---------------------------------------------------------
# TELEMETRY HISTORY ROUTER
# ---------------------------------------------------------


def test_history_returns_successful_empty_response(
    client,
    telemetry_service,
):
    telemetry_service.get_history.return_value = []

    response = client.get(
        "/api/factories/factory-01/motors/motor-01/telemetry",
        params={
            "start": "2026-11-25T17:00:00+00:00",
            "end": "2026-11-25T19:00:00+00:00",
            "limit": 100,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["factory_id"] == "factory-01"
    assert body["motor_id"] == "motor-01"
    assert body["count"] == 0
    assert body["limit"] == 100
    assert body["items"] == []


def test_history_returns_404_for_unknown_motor(
    client,
    telemetry_service,
):
    telemetry_service.get_history.side_effect = LookupError(
        "Motor not found"
    )

    response = client.get(
        "/api/factories/factory-01/motors/motor-999/telemetry",
        params={
            "start": "2026-11-25T17:00:00+00:00",
            "end": "2026-11-25T19:00:00+00:00",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Motor not found"


def test_history_rejects_timezone_naive_datetime(client):
    response = client.get(
        "/api/factories/factory-01/motors/motor-01/telemetry",
        params={
            "start": "2026-11-25T17:00:00",
            "end": "2026-11-25T19:00:00+00:00",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "start must contain a timezone"


def test_history_rejects_end_before_start(client):
    response = client.get(
        "/api/factories/factory-01/motors/motor-01/telemetry",
        params={
            "start": "2026-11-25T19:00:00+00:00",
            "end": "2026-11-25T17:00:00+00:00",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "start must be earlier than end"
    )


def test_history_rejects_invalid_limit(client):
    response = client.get(
        "/api/factories/factory-01/motors/motor-01/telemetry",
        params={
            "start": "2026-11-25T17:00:00+00:00",
            "end": "2026-11-25T19:00:00+00:00",
            "limit": 5001,
        },
    )

    assert response.status_code == 422
