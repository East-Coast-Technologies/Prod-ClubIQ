from flask import Blueprint

from .routes import register_routes
from .v1_routes import register_v1_routes


def create_members_blueprint(name="members", url_prefix="/members"):
    """
    Legacy members blueprint.

    Keeps existing multi-club routes:
    - /api/members/
    - /api/members/<member_id>
    """
    bp = Blueprint(name, __name__, url_prefix=url_prefix)
    register_routes(bp)
    return bp


def create_v1_members_blueprint(name="members_v1", url_prefix="/members"):
    """
    v1 single-club members blueprint.

    Exposes:
    - GET    /api/v1/members/
    - POST   /api/v1/members/
    - GET    /api/v1/members/<member_id>
    - PUT    /api/v1/members/<member_id>
    - DELETE /api/v1/members/<member_id>

    Does not expose frontend-controlled club_id.
    """
    bp = Blueprint(name, __name__, url_prefix=url_prefix)
    register_v1_routes(bp)
    return bp


# Legacy blueprint.
members_bp = create_members_blueprint(
    name="members",
    url_prefix="/api/members"
)
