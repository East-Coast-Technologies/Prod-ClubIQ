from flask import Blueprint
from .routes import register_routes


def create_activities_blueprint(name="activities", url_prefix="/activities"):
    """
    Blueprint factory for activity routes.

    This lets us mount the same activities implementation under:
    - legacy route: /api/activities
    - v1 route:     /api/v1/activities

    No business logic belongs here.
    """
    bp = Blueprint(name, __name__, url_prefix=url_prefix)
    register_routes(bp)
    return bp


# Legacy blueprint.
# Kept temporarily so existing frontend/tests do not break while v1 is introduced.
activities_bp = create_activities_blueprint(
    name="activities",
    url_prefix="/api/activities"
)
