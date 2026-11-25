
from fastapi.testclient import TestClient

from backend.api.app import app


def test_api_health_returns_healthy():
    with TestClient(app) as client:
        response = client.get("/api/health")

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "healthy"
    assert body["service"] == "motorguard-api"


def test_health_response_structure():
    with TestClient(app) as client:
        response = client.get("/api/health")

    assert response.status_code == 200

    body = response.json()

    assert "status" in body
    assert "service" in body
