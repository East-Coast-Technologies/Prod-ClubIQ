from flask_restful import Api
from app.clubs.v1_resources import V1ClubResource


def register_v1_routes(bp):
    api = Api(bp)

    # /api/v1/club
    # /api/v1/club/
    api.add_resource(V1ClubResource, "/")
