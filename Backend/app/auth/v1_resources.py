from flask import g
from flask_restful import Resource

from app.auth.decorators import auth_required
from app.auth.service import AuthService


class V1AuthMeResource(Resource):
    """
    v1 current-user context endpoint.

    GET /api/v1/auth/me

    The frontend does not send user_id.
    The backend resolves the current user from the verified Clerk token.
    """

    @auth_required()
    def get(self):
        return AuthService.get_v1_auth_context(g.current_user)
