from flask import Blueprint
from flask_restful import Api, Resource


class HealthResource(Resource):
    """
    Basic API health check and backend liveness probe endpoint used by Docker Compose.
    Keep this lightweight: no auth, no database, no external service checks.
    """

    def get(self):
        return {
            "status": "healthy",
            "message": "It feels good up here",
        }, 200


def create_health_blueprint(name="health", url_prefix="/health"):
    """
    Blueprint factory.

    This allows the same health resource to be mounted under:
    - legacy route: /api/health
    - v1 route:     /api/v1/health

    Later, when legacy routes are removed, v1 can stay untouched.
    """
    bp = Blueprint(name, __name__, url_prefix=url_prefix)
    api = Api(bp)

    api.add_resource(HealthResource, "/")

    return bp


# Legacy blueprint combining Docker Compose liveness probes and legacy API health.
# Keep this temporarily so existing tests/routes do not break while v1 is added.
health_bp = Blueprint("health", __name__)
api = Api(health_bp)

api.add_resource(
    HealthResource,
    "/api/health",
    "/api/health/",
    "/backend-health",
    "/backend-health/",
    "/api/backend-health",
    "/api/backend-health/",
)
