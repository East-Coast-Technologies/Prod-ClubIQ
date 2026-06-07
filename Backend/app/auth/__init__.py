from flask import Blueprint
from .routes import register_routes


def create_auth_blueprint(name="auth", url_prefix="/auth"):
    """
    Blueprint factory for auth routes.

    This lets us mount the same auth implementation under:
    - legacy route: /api/auth
    - v1 route:     /api/v1/auth

    Do not put business logic here.
    """
    bp = Blueprint(name, __name__, url_prefix=url_prefix)
    register_routes(bp)
    return bp


# Legacy blueprint.
# Kept temporarily so existing frontend/tests do not break while v1 is introduced.
auth_bp = create_auth_blueprint(
    name="auth",
    url_prefix="/api/auth"
)
