from flask import Blueprint

from .routes import register_routes
from .v1_routes import register_v1_routes


def create_auth_blueprint(name="auth", url_prefix="/auth"):
    """
    Legacy auth blueprint.

    Keeps existing routes:
    - /api/auth/sync/
    - /api/auth/me/<user_id>/
    - /api/auth/test/
    """
    bp = Blueprint(name, __name__, url_prefix=url_prefix)
    register_routes(bp)
    return bp


def create_v1_auth_blueprint(name="auth_v1", url_prefix="/auth"):
    """
    v1 auth blueprint.

    Exposes:
    - /api/v1/auth/sync/
    - /api/v1/auth/me
    - /api/v1/auth/test/

    Does not require frontend-provided user_id.
    """
    bp = Blueprint(name, __name__, url_prefix=url_prefix)
    register_v1_routes(bp)
    return bp


# Legacy blueprint.
auth_bp = create_auth_blueprint(
    name="auth",
    url_prefix="/api/auth"
)
