
from fastapi.testclient import TestClient

from backend.api.app import app


EXPECTED_ROUTES = {
    "/api/health": {"GET"},
    "/api/health/ready": {"GET"},
    "/api/factories": {"GET"},
    "/api/factories/{factory_id}": {"GET"},
    "/api/factories/{factory_id}/lines": {"GET"},
    "/api/factories/{factory_id}/lines/{line_id}": {"GET"},
    "/api/factories/{factory_id}/lines/{line_id}/motors": {"GET"},
    "/api/factories/{factory_id}/motors/{motor_id}": {"GET"},
    "/api/motors": {"GET"},
    "/api/factories/{factory_id}/motors/{motor_id}/telemetry/latest": {"GET"},
    "/api/factories/{factory_id}/motors/{motor_id}/telemetry": {"GET"},
    "/api/factories/{factory_id}/motors/{motor_id}/maintenance": {
        "GET",
        "POST",
    },
}


def test_openapi_is_available():
    with TestClient(app) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200

    body = response.json()

    assert "paths" in body
    assert "info" in body


def test_expected_routes_and_methods_are_registered():
    with TestClient(app) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200

    paths = response.json()["paths"]

    for path, expected_methods in EXPECTED_ROUTES.items():
        assert path in paths, f"Missing API route: {path}"

        actual_methods = {
            method.upper()
            for method in paths[path]
            if method.lower() in {"get", "post", "put", "patch", "delete"}
        }

        for method in expected_methods:
            assert method in actual_methods, (
                f"Missing {method} method for {path}"
            )
