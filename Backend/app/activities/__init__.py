from flask import Blueprint

from .routes import register_routes
from .v1_routes import register_v1_routes


def create_activities_blueprint(name="activities", url_prefix="/activities"):
    """
    Legacy activities blueprint.

    Keeps existing multi-club routes:
    - /api/activities/create/
    - /api/activities/<club_id>/
    """
    bp = Blueprint(name, __name__, url_prefix=url_prefix)
    register_routes(bp)
    return bp


def create_v1_activities_blueprint(name="activities_v1", url_prefix="/activities"):
    """
    v1 single-club activities blueprint.

    Exposes:
    - GET  /api/v1/activities/
    - POST /api/v1/activities/

    Does not expose frontend-controlled club_id.
    """
    bp = Blueprint(name, __name__, url_prefix=url_prefix)
    register_v1_routes(bp)
    return bp


# Legacy blueprint.
activities_bp = create_activities_blueprint(
    name="activities",
    url_prefix="/api/activities"
)
