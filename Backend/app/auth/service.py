"""
AuthService: Business logic for user authentication and sync.

Responsibilities:
- Create or update users in the database
- Ensure required fields are present
- Optional security: restrict sync to the currently logged-in user
"""

from app import db
from flask import current_app
from app.models import User, Club, ClubMember
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError


class AuthService:
    """
    Service class for authentication-related business logic.
    """

    @staticmethod
    def sync_user(data: dict, current_user: User = None):
        """
        Create or update a user in the database.

        Args:
            data (dict): User data from Clerk. Must include:
                         'clerk_id', 'name', 'email', 'username', 'role'.
            current_user (User, optional): Authenticated user making the request.
                                           If provided, prevents syncing another user.

        Returns:
            tuple: (response_dict, HTTP status code)
        """
        if not data:
            return {"message": "No user data provided"}, 400

        # Required fields
        required_fields = ("clerk_id", "name", "email", "username", "role")
        for field in required_fields:
            if not data.get(field):
                return {"message": f"{field} is required"}, 400

        # Optional security: enforce that current_user can only sync themselves
        if current_user:
            data["clerk_id"] = current_user.clerk_id
            data["email"] = current_user.email

        # Check if user already exists by clerk_id or email
        existing_user = User.query.filter(
            or_(User.clerk_id == data.get("clerk_id"),
                User.email == data.get("email"))
        ).first()

        if existing_user:
            # Update existing user
            existing_user.name = data.get("name")
            existing_user.username = data.get("username")
            existing_user.role = data.get("role", existing_user.role)
            synced_user = existing_user
            message = "User updated successfully"
        else:
            # Create new user
            synced_user = User(
                clerk_id=data.get("clerk_id"),
                name=data.get("name"),
                email=data.get("email"),
                username=data.get("username"),
                role=data.get("role")
            )
            db.session.add(synced_user)
            message = "User created successfully"

        # Commit changes to database
        try:
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            return {
                "message": "User sync failed due to duplicate email/username/clerk_id",
                "error": str(exc.orig),
            }, 409
        except Exception as exc:
            db.session.rollback()
            return {
                "message": "User sync failed",
                "error": str(exc),
            }, 500

        return {
            "message": message,
            "user": synced_user.to_dict(),
            "verified_via": "Clerk"
        }, 200


    @staticmethod
    def get_v1_auth_context(current_user: User):
        """
        Return the authenticated user's v1 app context.

        v1 is single-club:
        - user comes from Clerk-authenticated session
        - club comes from SINGLE_CLUB_NAME
        - membership is looked up inside that configured club
        """
        if not current_user:
            return {"message": "User not synced"}, 403

        single_club_name = current_app.config.get("SINGLE_CLUB_NAME")

        if not single_club_name:
            return {"message": "SINGLE_CLUB_NAME is not configured"}, 500

        club = Club.query.filter_by(name=single_club_name).first()

        if not club:
            return {"message": "Configured club was not found"}, 404

        membership = ClubMember.query.filter_by(
            club_id=club.id,
            user_id=current_user.id,
        ).first()

        return {
            "user": current_user.to_dict(),
            "club": {
                "id": str(club.id),
                "name": club.name,
                "description": club.description,
            },
            "member": {
            "id": str(membership.id),
            "club_id": str(membership.club_id),
            "user_id": membership.user_id,
            "username": membership.user.username if membership.user else None,
            "role": membership.role,
            "joined_at": membership.joined_at.isoformat() if membership.joined_at else None,
        } if membership else None,
            "access": {
                "is_member": membership is not None,
                "role": membership.role if membership else None,
            },
        }, 200
