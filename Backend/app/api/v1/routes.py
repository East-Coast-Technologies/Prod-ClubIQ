from flask import Blueprint

from app.health.routes import create_health_blueprint
from app.auth import create_auth_blueprint
from app.members import create_members_blueprint


api_v1_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")


# v1 public routes
api_v1_bp.register_blueprint(
    create_health_blueprint(
        name="health_v1",
        url_prefix="/health"
    )
)

api_v1_bp.register_blueprint(
    create_auth_blueprint(
        name="auth_v1",
        url_prefix="/auth"
    )
)

api_v1_bp.register_blueprint(
    create_members_blueprint(
        name="members_v1",
        url_prefix="/members"
    )
)
