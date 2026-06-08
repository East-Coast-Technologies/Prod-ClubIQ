from flask import Blueprint

from .routes import register_blueprints
from .v1_routes import register_v1_routes


def create_clubs_blueprint(name="clubs", url_prefix="/clubs"):
    """
    Legacy multi-club blueprint.

    This is kept for existing routes/tests while v1 is introduced.
    Do not expose this full multi-club API under /api/v1.
    """
    bp = Blueprint(name, __name__, url_prefix=url_prefix)
    register_blueprints(bp)
    return bp


def create_v1_club_blueprint(name="club_v1", url_prefix="/club"):
    """
    v1 single-club blueprint.

    Exposes:
    - GET /api/v1/club

    Does not expose:
    - POST /api/v1/clubs
    - GET /api/v1/clubs
    - PUT /api/v1/clubs/<club_id>
    - DELETE /api/v1/clubs/<club_id>
    """
    bp = Blueprint(name, __name__, url_prefix=url_prefix)
    register_v1_routes(bp)
    return bp


# Legacy blueprint.
# Kept temporarily so existing frontend/tests do not break while v1 is introduced.
clubs_bp = create_clubs_blueprint(
    name="clubs",
    url_prefix="/api/clubs"
)
