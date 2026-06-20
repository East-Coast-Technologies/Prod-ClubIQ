from app import create_app
from config import TestingConfig


class LegacyDisabledTestingConfig(TestingConfig):
    EXPOSE_LEGACY_API = False


def test_health_endpoints_hybrid_response(client):
    """
    Test that all the different iterations of health routes (legacy, Docker, v1)
    return the hybrid health check response correctly.
    """
    endpoints = [
        "/api/health",
        "/api/health/",
        "/backend-health",
        "/backend-health/",
        "/api/backend-health",
        "/api/backend-health/",
        "/api/v1/health/",
    ]

    expected_json = {"status": "healthy", "message": "It feels good up here"}

    for endpoint in endpoints:
        resp = client.get(endpoint)
        assert resp.status_code == 200, (
            f"Endpoint {endpoint} failed with status {resp.status_code}"
        )
        assert resp.get_json() == expected_json, (
            f"Endpoint {endpoint} returned unexpected JSON: {resp.get_json()}"
        )


def test_backend_liveness_route_stays_available_when_legacy_api_disabled():
    app = create_app(LegacyDisabledTestingConfig)
    client = app.test_client()

    resp = client.get("/api/backend-health")

    assert resp.status_code == 200
    assert resp.get_json() == {
        "status": "healthy",
        "message": "It feels good up here",
    }
