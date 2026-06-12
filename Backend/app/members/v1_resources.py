from flask import request, g
from flask_restful import Resource

from app.auth.decorators import auth_required
from app.members.service import MemberService


class V1MemberResource(Resource):
    """
    v1 single-club member detail endpoint.

    Detail operations still use membership id.
    The club boundary is enforced by service methods.
    """

    @auth_required()
    def get(self, member_id):
        return MemberService.get_member(member_id)

    @auth_required()
    def put(self, member_id):
        data = request.get_json() or {}
        return MemberService.update_member(member_id, data, g.current_user)

    @auth_required()
    def delete(self, member_id):
        return MemberService.delete_member(member_id, g.current_user)


class V1MemberListResource(Resource):
    """
    v1 single-club members collection.

    GET  /api/v1/members/
    POST /api/v1/members/

    v1 does not accept club_id from the frontend.
    """

    @auth_required()
    def get(self):
        if "club_id" in request.args:
            return {"error": "club_id query param is not accepted in v1"}, 400

        mine = request.args.get("mine", "false").lower() in ["1", "true", "yes"]
        return MemberService.list_v1_members(g.current_user, mine=mine)

    @auth_required()
    def post(self):
        data = request.get_json() or {}
        return MemberService.create_v1_member(data, g.current_user)
