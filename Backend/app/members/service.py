from uuid import UUID
from flask import current_app
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import ClubMember, Club, User


def _parse_uuid(value):
    try:
        return UUID(str(value))
    except (ValueError, TypeError):
        return None


class MemberService:
    @staticmethod
    def _member_to_dict(member: ClubMember):
        return {
            "id": str(member.id),
            "club_id": str(member.club_id),
            "user_id": member.user_id,
            "username": member.user.username if member.user else None,
            "role": member.role,
            "joined_at": member.joined_at.isoformat() if member.joined_at else None,
        }


    @staticmethod
    def _get_v1_active_club():
        """
        Resolve the single active club for v1.

        v1 does not accept club_id from the frontend.
        The active club is controlled by SINGLE_CLUB_NAME.
        """
        single_club_name = current_app.config.get("SINGLE_CLUB_NAME")

        if not single_club_name:
            return None, {"error": "SINGLE_CLUB_NAME is not configured"}, 500

        club = Club.query.filter_by(name=single_club_name).first()

        if not club:
            return None, {"error": "Configured club was not found"}, 404

        return club, None, None

    @staticmethod
    def list_v1_members(current_user, mine: bool = False):
        """
        List members for the configured v1 club only.
        """
        club, error, status = MemberService._get_v1_active_club()
        if error:
            return error, status

        return MemberService.list_members(
            current_user,
            mine=mine,
            club_id=str(club.id),
        )

    @staticmethod
    def create_v1_member(data, current_user):
        """
        Create a member under the configured v1 club.

        The frontend must not send club_id in v1.
        """
        data = data or {}

        if "club_id" in data:
            return {"error": "club_id is not accepted in v1"}, 400

        club, error, status = MemberService._get_v1_active_club()
        if error:
            return error, status

        v1_data = {
            **data,
            "club_id": str(club.id),
        }

        return MemberService.create_member(v1_data, current_user)


    @staticmethod
    def list_members(current_user, mine: bool = False, club_id=None):
        query = ClubMember.query

        if club_id:
            club_uuid = _parse_uuid(club_id)
            if not club_uuid:
                return {"error": "Invalid club_id"}, 400
            query = query.filter(ClubMember.club_id == club_uuid)

        if mine and current_user.role not in ["admin", "super_user"]:
            query = query.join(Club, Club.id == ClubMember.club_id).filter(
                (ClubMember.user_id == current_user.id) | (Club.created_by == current_user.id)
            )

        members = query.all()
        return [MemberService._member_to_dict(m) for m in members], 200

    @staticmethod
    def get_member(member_id):
        member_uuid = _parse_uuid(member_id)
        if not member_uuid:
            return {"message": "Member not found"}, 404

        member = db.session.get(ClubMember, member_uuid)
        if not member:
            return {"message": "Member not found"}, 404

        return MemberService._member_to_dict(member), 200

    @staticmethod
    def _ensure_club_and_user(club_id, user_id):
        club_uuid = _parse_uuid(club_id)
        if not club_uuid:
            return None, None, ({"error": "Invalid club_id"}, 400)

        club = db.session.get(Club, club_uuid)
        if not club:
            return None, None, ({"error": "Club not found"}, 404)

        user = db.session.get(User, user_id)
        if not user:
            return None, None, ({"error": "User not found"}, 404)

        return club, user, None

    @staticmethod
    def _authorized(user, club):
        return user and (user.role in ["admin", "super_user"] or club.created_by == user.id)

    @staticmethod
    def create_member(data, current_user):
        required = ["club_id", "user_id"]
        missing = [f for f in required if not data.get(f)]
        if missing:
            return {"error": f"Missing field(s): {', '.join(missing)}"}, 400

        club, user, err = MemberService._ensure_club_and_user(data.get("club_id"), data.get("user_id"))
        if err:
            return err

        if not MemberService._authorized(current_user, club):
            return {"error": "Access forbidden: Insufficient permissions"}, 403

        existing = ClubMember.query.filter_by(club_id=club.id, user_id=user.id).first()
        if existing:
            return {"error": "User already a member of this club"}, 400

        role = data.get("role", "member")

        new_member = ClubMember(club_id=club.id, user_id=user.id, role=role)
        db.session.add(new_member)

        try:
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            return {"error": "Member creation failed", "details": str(exc.orig)}, 409
        except Exception as exc:
            db.session.rollback()
            return {"error": "Member creation failed", "details": str(exc)}, 500

        return {"message": "Member created successfully", **MemberService._member_to_dict(new_member)}, 201

    @staticmethod
    def update_member(member_id, data, current_user):
        member_uuid = _parse_uuid(member_id)
        if not member_uuid:
            return {"error": "Member not found"}, 404

        member = db.session.get(ClubMember, member_uuid)
        if not member:
            return {"error": "Member not found"}, 404

        club = db.session.get(Club, member.club_id)
        if not MemberService._authorized(current_user, club):
            return {"error": "Access forbidden: Insufficient permissions"}, 403

        if "role" in data:
            member.role = data["role"]

        try:
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            return {"error": "Member update failed", "details": str(exc.orig)}, 409
        except Exception as exc:
            db.session.rollback()
            return {"error": "Member update failed", "details": str(exc)}, 500

        return {"message": "Member updated successfully", **MemberService._member_to_dict(member)}, 200

    @staticmethod
    def delete_member(member_id, current_user):
        member_uuid = _parse_uuid(member_id)
        if not member_uuid:
            return {"error": "Member not found"}, 404

        member = db.session.get(ClubMember, member_uuid)
        if not member:
            return {"error": "Member not found"}, 404

        club = db.session.get(Club, member.club_id)
        if not MemberService._authorized(current_user, club):
            return {"error": "Access forbidden: Insufficient permissions"}, 403

        db.session.delete(member)

        try:
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            return {"error": "Member deletion failed", "details": str(exc.orig)}, 409
        except Exception as exc:
            db.session.rollback()
            return {"error": "Member deletion failed", "details": str(exc)}, 500

        return {"message": "Member deleted successfully"}, 200
