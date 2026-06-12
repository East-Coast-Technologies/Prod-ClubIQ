from flask_restful import Api

from app.activities.v1_resources import V1ActivityListResource


def register_v1_routes(bp):
    api = Api(bp)

    # Supports both:
    # /api/v1/activities
    # /api/v1/activities/
    api.add_resource(V1ActivityListResource, "", "/")
