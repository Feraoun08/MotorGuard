from datetime import datetime, timezone
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.dependencies import get_db_session
from backend.api.routers.diagnosis import router
from backend.api.services.diagnosis_service import DiagnosisService
from backend.ml.feature_extractor import FeatureExtractionError


def create_test_app():

    app = FastAPI()

    app.include_router(router)

    app.state.influx_store = MagicMock()
    app.state.model_loader = MagicMock()

    app.dependency_overrides[get_db_session] = lambda: MagicMock()

    return app


def test_diagnosis_endpoint_success(monkeypatch):

    expected_response = {
        "factory_id": "factory-01",
        "line_id": "line-01",
        "motor_id": "motor-01",
        "timestamp": datetime.now(timezone.utc),
        "predicted_class": "IR_007_1",
        "confidence": 0.95,
        "ground_truth": "Normal_1",
        "is_simulated": True,
    }

    mock_service = MagicMock()

    mock_service.diagnose.return_value = expected_response

    monkeypatch.setattr(
        "backend.api.routers.diagnosis.build_service",
        lambda request, session: mock_service,
    )

    app = create_test_app()

    client = TestClient(app)

    response = client.get(
        "/api/factories/factory-01/motors/motor-01/diagnosis"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["factory_id"] == "factory-01"
    assert body["motor_id"] == "motor-01"
    assert body["predicted_class"] == "IR_007_1"
    assert body["confidence"] == 0.95
    assert body["ground_truth"] == "Normal_1"

    mock_service.diagnose.assert_called_once_with(
        factory_id="factory-01",
        motor_id="motor-01",
    )


def test_diagnosis_endpoint_motor_not_found(monkeypatch):

    mock_service = MagicMock()

    mock_service.diagnose.side_effect = LookupError(
        "Motor not found"
    )

    monkeypatch.setattr(
        "backend.api.routers.diagnosis.build_service",
        lambda request, session: mock_service,
    )

    app = create_test_app()

    client = TestClient(app)

    response = client.get(
        "/api/factories/unknown/motors/unknown/diagnosis"
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Motor not found"


def test_diagnosis_endpoint_no_telemetry(monkeypatch):

    mock_service = MagicMock()

    mock_service.diagnose.side_effect = LookupError(
        "No telemetry available for this motor"
    )

    monkeypatch.setattr(
        "backend.api.routers.diagnosis.build_service",
        lambda request, session: mock_service,
    )

    app = create_test_app()

    client = TestClient(app)

    response = client.get(
        "/api/factories/factory-01/motors/motor-01/diagnosis"
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "No telemetry available for this motor"
    )


def test_diagnosis_endpoint_invalid_features(monkeypatch):

    mock_service = MagicMock()

    mock_service.diagnose.side_effect = FeatureExtractionError(
        "Feature 'rms' is not finite"
    )

    monkeypatch.setattr(
        "backend.api.routers.diagnosis.build_service",
        lambda request, session: mock_service,
    )

    app = create_test_app()

    client = TestClient(app)

    response = client.get(
        "/api/factories/factory-01/motors/motor-01/diagnosis"
    )

    assert response.status_code == 422

    assert response.json()["detail"] == (
        "Feature 'rms' is not finite"
    )