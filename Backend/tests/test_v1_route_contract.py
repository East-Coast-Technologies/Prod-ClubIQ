from app import create_app
from config import TestingConfig


def _routes():
    app = create_app(TestingConfig)
    return {str(rule) for rule in app.url_map.iter_rules()}


def test_v1_does_not_expose_local_invitations_api():
    routes = _routes()

    assert "/api/v1/invitations/" not in routes
    assert "/api/v1/invitations/<int:invite_id>" not in routes
    assert "/api/v1/invitations/<string:token>/accept" not in routes


def test_v1_does_not_expose_multi_club_collection_api():
    routes = _routes()

    assert "/api/v1/clubs/" not in routes
    assert "/api/v1/clubs/<string:club_id>" not in routes


def test_v1_exposes_single_club_api_only():
    routes = _routes()

    assert "/api/v1/club/" in routes
