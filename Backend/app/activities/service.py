from uuid import UUID
from flask import current_app
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import Activity, Club


def _parse_uuid(value):
    try:
        return UUID(str(value))
    except (ValueError, TypeError):
        return None

class ActivityService:
    # Removes author, to be implemented Some other time
    
    @staticmethod
    def _get_v1_active_club():
        """
        Resolve the single active club for v1.

        v1 does not accept club_id from the frontend.
        The active club is controlled by SINGLE_CLUB_NAME.
        """
        single_club_name = current_app.config.get("SINGLE_CLUB_NAME")

        if not single_club_name:
            return None, {"message": "SINGLE_CLUB_NAME is not configured"}, 500

        club = Club.query.filter_by(name=single_club_name).first()

        if not club:
            return None, {"message": "Configured club was not found"}, 404

        return club, None, None


    @staticmethod
    def _can_access_v1_club(current_user, club):
        """
        Return True when the current user can access v1 club data.

        Allowed:
        - configured club creator
        - admin
        - super_user
        - member of configured club
        """
        if not current_user:
            return False

        if current_user.role in ["admin", "super_user"]:
            return True

        if club.created_by == current_user.id:
            return True

        from app.models import ClubMember

        membership = ClubMember.query.filter_by(
            club_id=club.id,
            user_id=current_user.id,
        ).first()

        return membership is not None


    @staticmethod
    def create_v1_activity(data, current_user):
        """
        Create an activity for the configured v1 club.

        The frontend must not send club_id in v1.
        """
        data = data or {}

        if "club_id" in data:
            return {"message": "club_id is not accepted in v1"}, 400

        club, error, status = ActivityService._get_v1_active_club()
        if error:
            return error, status

        v1_data = {
            **data,
            "club_id": str(club.id),
        }

        return ActivityService.create_activity(v1_data, current_user)


    ython

    @staticmethod
    def list_v1_activities(current_user):
        """
        List activities for the configured v1 club.

        Synced users who are not part of the configured club cannot read
        v1 club activity data.
        """
        club, error, status = ActivityService._get_v1_active_club()
        if error:
            return error, status

        if not ActivityService._can_access_v1_club(current_user, club):
            return {"message": "User is not a member of the configured club"}, 403

        return ActivityService.list_activities(str(club.id))


    @staticmethod
    def create_activity(data, current_user):
        title = data.get("title")
        description = data.get("description")
        club_id = data.get("club_id")

        if not title:
            return {"message": "Title is required"}, 400
        if not club_id:
            return {"message": "club_id is required"}, 400

        club_uuid = _parse_uuid(club_id)
        if not club_uuid:
            return {"message": "Invalid club_id"}, 400

        club = db.session.get(Club, club_uuid)
        if not club:
            return {"message": "Club not found"}, 404

        if not current_user:
            return {"message": "User not synced"}, 403

        if current_user.role not in ["admin", "super_user"] and club.created_by != current_user.id:
            return {"message": "Access forbidden: Insufficient permissions"}, 403

        if Activity.query.filter_by(title=title, club_id=club.id).first():
            return {"message": "Activity already exists for this club"}, 400

        activity = Activity(
            title=title,
            description=description,
            club_id=club.id,
            author_id=current_user.id,
        )

        db.session.add(activity)

        try:
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            return {"message": "Activity creation failed", "error": str(exc.orig)}, 409
        except Exception as exc:
            db.session.rollback()
            return {"message": "Activity creation failed", "error": str(exc)}, 500

        return {
            "message": "Activity created successfully",
            "Details": ActivityService._serialize(activity)
        }, 201
        
        
    @staticmethod
    def list_activities(club_id):
        club_uuid = _parse_uuid(club_id)
        if not club_uuid:
            return {"message": "Club not found"}, 404

        club = db.session.get(Club, club_uuid)
        if not club:
            return {"message": "Club not found"}, 404

        activities = (
            Activity.query.filter_by(club_id=club.id)
            .order_by(Activity.created_at.desc())
            .all()
        )

        return [ActivityService._serialize(a) for a in activities], 200
        
        
    @staticmethod
    def _serialize(activity):
        return {
            "id": str(activity.id), 
            "club_id": str(activity.club_id) if activity.club_id else None,
            "title": activity.title,
            "description": activity.description,
            "created_by": activity.author.username if activity.author else None,
            "created_at": activity.created_at.isoformat() if activity.created_at else None,
            "start_date": activity.start_date.isoformat() if activity.start_date else None,
        }
        
        
        
