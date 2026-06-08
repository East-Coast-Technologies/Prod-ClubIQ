from flask import Blueprint

from app.health.routes import create_health_blueprint
from app.auth import create_auth_blueprint
from app.members import create_members_blueprint
from app.activities import create_activities_blueprint
from app.rating import create_ratings_blueprint
from app.clubs import create_v1_club_blueprint


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

api_v1_bp.register_blueprint(
    create_activities_blueprint(
        name="activities_v1",
        url_prefix="/activities"
    )
)

api_v1_bp.register_blueprint(
    create_ratings_blueprint(
        name="ratings_v1",
        url_prefix="/ratings"
    )
)

api_v1_bp.register_blueprint(
    create_v1_club_blueprint(
        name="club_v1",
        url_prefix="/club"
    )
)
