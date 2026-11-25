
from datetime import datetime, timezone
from uuid import uuid4
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from backend.api.services.maintenance_service import MaintenanceService
from backend.api.schemas.maintenance import MaintenanceCreate
from backend.api.dependencies import get_db_session
from backend.api.app import app
import backend.api.routers.maintenance as maintenance_router


# =========================================================
# SHARED FIXTURES
# =========================================================


@pytest.fixture
def session():
    return Mock()


@pytest.fixture
def sample_motor():
    return Mock(
        factory_id="factory-01",
        id="motor-01",
        line_id="line-01",
        name="Motor 01",
    )


@pytest.fixture
def sample_maintenance():
    return Mock(
        id=uuid4(),
        factory_id="factory-01",
        motor_id="motor-01",
        maintenance_type="inspection",
        description="Bearing inspection",
        performed_at=datetime(
            2026, 11, 25, 17, 0, 0,
            tzinfo=timezone.utc,
        ),
        created_at=datetime(
            2026, 11, 25, 17, 5, 0,
            tzinfo=timezone.utc,
        ),
    )


@pytest.fixture
def maintenance_payload():
    return MaintenanceCreate(
        maintenance_type="inspection",
        description="Bearing inspection",
        performed_at=datetime(
            2026, 11, 25, 17, 0, 0,
            tzinfo=timezone.utc,
        ),
    )


# =========================================================
# SERVICE TESTS
# =========================================================


def test_get_motor_returns_motor_when_found(
    session,
    sample_motor,
):
    session.execute.return_value.scalar_one_or_none.return_value = (
        sample_motor
    )

    service = MaintenanceService(session)

    result = service.get_motor(
        factory_id="factory-01",
        motor_id="motor-01",
    )

    assert result is sample_motor
    session.execute.assert_called_once()


def test_get_motor_returns_none_when_not_found(session):
    session.execute.return_value.scalar_one_or_none.return_value = None

    service = MaintenanceService(session)

    result = service.get_motor(
        factory_id="factory-01",
        motor_id="motor-999",
    )

    assert result is None


def test_get_maintenance_history_returns_records(
    session,
    sample_motor,
    sample_maintenance,
):
    motor_result = Mock()
    motor_result.scalar_one_or_none.return_value = sample_motor

    history_result = Mock()
    history_result.scalars.return_value.all.return_value = [
        sample_maintenance
    ]

    session.execute.side_effect = [
        motor_result,
        history_result,
    ]

    service = MaintenanceService(session)

    result = service.get_maintenance_history(
        factory_id="factory-01",
        motor_id="motor-01",
    )

    assert len(result) == 1
    assert result[0] is sample_maintenance
    assert session.execute.call_count == 2


def test_get_maintenance_history_returns_empty_list(
    session,
    sample_motor,
):
    motor_result = Mock()
    motor_result.scalar_one_or_none.return_value = sample_motor

    history_result = Mock()
    history_result.scalars.return_value.all.return_value = []

    session.execute.side_effect = [
        motor_result,
        history_result,
    ]

    service = MaintenanceService(session)

    result = service.get_maintenance_history(
        factory_id="factory-01",
        motor_id="motor-01",
    )

    assert result == []


def test_get_maintenance_history_returns_none_for_unknown_motor(
    session,
):
    session.execute.return_value.scalar_one_or_none.return_value = None

    service = MaintenanceService(session)

    result = service.get_maintenance_history(
        factory_id="factory-01",
        motor_id="motor-999",
    )

    assert result is None

    # Only the motor existence query should have been executed.
    assert session.execute.call_count == 1


def test_create_maintenance_success(
    session,
    sample_motor,
    maintenance_payload,
):
    session.execute.return_value.scalar_one_or_none.return_value = (
        sample_motor
    )

    service = MaintenanceService(session)

    result = service.create_maintenance(
        factory_id="factory-01",
        motor_id="motor-01",
        payload=maintenance_payload,
    )

    assert result is not None

    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(result)

    created_record = session.add.call_args.args[0]

    assert created_record.factory_id == "factory-01"
    assert created_record.motor_id == "motor-01"
    assert created_record.maintenance_type == "inspection"
    assert created_record.description == "Bearing inspection"
    assert created_record.performed_at == maintenance_payload.performed_at


def test_create_maintenance_returns_none_for_unknown_motor(
    session,
    maintenance_payload,
):
    session.execute.return_value.scalar_one_or_none.return_value = None

    service = MaintenanceService(session)

    result = service.create_maintenance(
        factory_id="factory-01",
        motor_id="motor-999",
        payload=maintenance_payload,
    )

    assert result is None

    session.add.assert_not_called()
    session.commit.assert_not_called()
    session.refresh.assert_not_called()


# =========================================================
# ROUTER TEST FIXTURES
# =========================================================


@pytest.fixture
def router_service():
    return Mock()


@pytest.fixture
def router_client(monkeypatch, router_service):
    monkeypatch.setattr(
        maintenance_router,
        "MaintenanceService",
        lambda session: router_service,
    )

    app.dependency_overrides[get_db_session] = lambda: Mock()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# =========================================================
# GET MAINTENANCE ROUTER TESTS
# =========================================================


def test_get_maintenance_history_returns_200(
    router_client,
    router_service,
    sample_maintenance,
):
    router_service.get_maintenance_history.return_value = [
        sample_maintenance
    ]

    response = router_client.get(
        "/api/factories/factory-01/motors/motor-01/maintenance"
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["factory_id"] == "factory-01"
    assert body[0]["motor_id"] == "motor-01"
    assert body[0]["maintenance_type"] == "inspection"
    assert body[0]["description"] == "Bearing inspection"


def test_get_maintenance_history_returns_empty_list(
    router_client,
    router_service,
):
    router_service.get_maintenance_history.return_value = []

    response = router_client.get(
        "/api/factories/factory-01/motors/motor-01/maintenance"
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_maintenance_history_returns_404_for_unknown_motor(
    router_client,
    router_service,
):
    router_service.get_maintenance_history.return_value = None

    response = router_client.get(
        "/api/factories/factory-01/motors/motor-999/maintenance"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Motor not found"


# =========================================================
# POST MAINTENANCE ROUTER TESTS
# =========================================================


def test_create_maintenance_returns_201(
    router_client,
    router_service,
    sample_maintenance,
):
    router_service.create_maintenance.return_value = (
        sample_maintenance
    )

    response = router_client.post(
        "/api/factories/factory-01/motors/motor-01/maintenance",
        json={
            "maintenance_type": "inspection",
            "description": "Bearing inspection",
            "performed_at": "2026-11-25T17:00:00+00:00",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["factory_id"] == "factory-01"
    assert body["motor_id"] == "motor-01"
    assert body["maintenance_type"] == "inspection"
    assert body["description"] == "Bearing inspection"
    assert "id" in body
    assert "created_at" in body


def test_create_maintenance_returns_404_for_unknown_motor(
    router_client,
    router_service,
):
    router_service.create_maintenance.return_value = None

    response = router_client.post(
        "/api/factories/factory-01/motors/motor-999/maintenance",
        json={
            "maintenance_type": "inspection",
            "description": "Bearing inspection",
            "performed_at": "2026-11-25T17:00:00+00:00",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Motor not found"


def test_create_maintenance_rejects_empty_maintenance_type(
    router_client,
):
    response = router_client.post(
        "/api/factories/factory-01/motors/motor-01/maintenance",
        json={
            "maintenance_type": "",
            "description": "Bearing inspection",
            "performed_at": "2026-11-25T17:00:00+00:00",
        },
    )

    assert response.status_code == 422


def test_create_maintenance_rejects_empty_description(
    router_client,
):
    response = router_client.post(
        "/api/factories/factory-01/motors/motor-01/maintenance",
        json={
            "maintenance_type": "inspection",
            "description": "",
            "performed_at": "2026-11-25T17:00:00+00:00",
        },
    )

    assert response.status_code == 422


def test_create_maintenance_rejects_missing_performed_at(
    router_client,
):
    response = router_client.post(
        "/api/factories/factory-01/motors/motor-01/maintenance",
        json={
            "maintenance_type": "inspection",
            "description": "Bearing inspection",
        },
    )

    assert response.status_code == 422


def test_create_maintenance_rejects_invalid_payload(
    router_client,
):
    response = router_client.post(
        "/api/factories/factory-01/motors/motor-01/maintenance",
        json={
            "maintenance_type": 123,
            "description": None,
            "performed_at": "not-a-date",
        },
    )

    assert response.status_code == 422
