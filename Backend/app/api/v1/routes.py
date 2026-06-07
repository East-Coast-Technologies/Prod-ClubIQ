from flask import Blueprint

from app.health.routes import create_health_blueprint


api_v1_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")


# v1 public routes
api_v1_bp.register_blueprint(
    create_health_blueprint(
        name="health_v1",
        url_prefix="/health"
    )
)
