from app import create_app
from config import TestingConfig


class LegacyDisabledTestingConfig(TestingConfig):
    EXPOSE_LEGACY_API = False


def _routes(config_class):
    app = create_app(config_class)
    return {str(rule) for rule in app.url_map.iter_rules()}


def test_legacy_api_routes_are_enabled_by_default_in_tests():
    routes = _routes(TestingConfig)

    assert "/api/auth/sync/" in routes
    assert "/api/clubs/" in routes
    assert "/api/members/" in routes
    assert "/api/activities/create/" in routes
    assert "/api/invitations/" in routes


def test_legacy_api_routes_can_be_disabled_for_production():
    routes = _routes(LegacyDisabledTestingConfig)

    assert "/api/auth/sync/" not in routes
    assert "/api/auth/me/<int:user_id>/" not in routes
    assert "/api/clubs/" not in routes
    assert "/api/clubs/<string:club_id>" not in routes
    assert "/api/members/" not in routes
    assert "/api/activities/create/" not in routes
    assert "/api/invitations/" not in routes
    assert "/api/health/" not in routes

    assert "/api/backend-health" in routes
    assert "/api/backend-health/" in routes
    assert "/api/v1/health/" in routes
    assert "/api/v1/auth/sync/" in routes
    assert "/api/v1/auth/me" in routes
    assert "/api/v1/club/" in routes
    assert "/api/v1/members/" in routes
    assert "/api/v1/activities/" in routes
