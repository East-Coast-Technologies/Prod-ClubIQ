from flask import request, g
from flask_restful import Resource

from app.activities.service import ActivityService
from app.auth.decorators import auth_required


class V1ActivityListResource(Resource):
    """
    v1 single-club activities endpoint.

    GET  /api/v1/activities/
    POST /api/v1/activities/

    v1 does not accept club_id from the frontend.
    """

    @auth_required()
    def get(self):
        return ActivityService.list_v1_activities(g.current_user)

    @auth_required()
    def post(self):
        data = request.get_json() or {}
        return ActivityService.create_v1_activity(data, g.current_user)
