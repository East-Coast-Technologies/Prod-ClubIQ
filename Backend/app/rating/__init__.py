from flask import Blueprint
from .routes import register_routes


def create_ratings_blueprint(name="ratings", url_prefix="/ratings"):
    """
    Blueprint factory for rating routes.

    This lets us mount the same ratings implementation under:
    - legacy route: /api/ratings
    - v1 route:     /api/v1/ratings

    Keep business logic in resources/services, not here.
    """
    bp = Blueprint(name, __name__, url_prefix=url_prefix)
    register_routes(bp)
    return bp


# Legacy blueprint.
# Kept temporarily so existing frontend/tests do not break while v1 is introduced.
ratings_bp = create_ratings_blueprint(
    name="ratings",
    url_prefix="/api/ratings"
)
