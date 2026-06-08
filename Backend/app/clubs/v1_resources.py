from flask_restful import Resource
from app.auth.decorators import auth_required
from app.clubs.service import ClubService


class V1ClubResource(Resource):
    """
    v1 single-club endpoint.

    This endpoint returns the one active production club.
    It does not expose multi-club listing, creation, update, or deletion.
    """

    @auth_required()
    def get(self):
        return ClubService.get_v1_active_club()
