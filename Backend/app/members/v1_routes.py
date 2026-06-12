from flask_restful import Api

from app.members.v1_resources import V1MemberListResource, V1MemberResource


def register_v1_routes(bp):
    api = Api(bp)

    api.add_resource(V1MemberListResource, "/", "")
    api.add_resource(V1MemberResource, "/<string:member_id>")
