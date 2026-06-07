from flask import Blueprint
from .routes import register_routes


def create_members_blueprint(name="members", url_prefix="/members"):
    """
    Blueprint factory for member routes.

    This lets us mount the same members implementation under:
    - legacy route: /api/members
    - v1 route:     /api/v1/members

    Keep business logic in resources/services, not here.
    """
    bp = Blueprint(name, __name__, url_prefix=url_prefix)
    register_routes(bp)
    return bp


# Legacy blueprint.
# Kept temporarily so existing frontend/tests do not break while v1 is introduced.
members_bp = create_members_blueprint(
    name="members",
    url_prefix="/api/members"
)
