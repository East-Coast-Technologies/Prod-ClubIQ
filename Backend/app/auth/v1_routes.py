from flask_restful import Api

from app.auth.resources import SyncUserResource, TestAuthResource
from app.auth.v1_resources import V1AuthMeResource


def register_v1_routes(bp):
    api = Api(bp)

    api.add_resource(SyncUserResource, "/sync/")
    api.add_resource(V1AuthMeResource, "/me")
    api.add_resource(TestAuthResource, "/test/")
