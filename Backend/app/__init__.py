from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mail import Mail
from flask_apscheduler import APScheduler
from config import Config
from flask_migrate import Migrate
import os
# from app.models import User, Event, Member, Attendance, Project

# Initialize extensions outside the factory
db = SQLAlchemy()
restful_api = Api()
cors = CORS()
mail = Mail()
scheduler = APScheduler()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    if config_class is None:
        app.config.from_object(os.environ.get('FLASK_CONFIG_TYPE', 'default'))
    else:
        app.config.from_object(config_class)
    
    # Initialize extensions with the app instance
    db.init_app(app)
    migrate.init_app(app, db)
    restful_api.init_app(app)
    cors.init_app(app, supports_credentials=True)
    mail.init_app(app)
    scheduler.init_app(app)
    
    # Register v1 API routes
    from app.api.v1.routes import api_v1_bp
    app.register_blueprint(api_v1_bp)

    # Register legacy /api/... routes only when enabled.
    # Keep enabled for dev/tests.
    # Disable in production with EXPOSE_LEGACY_API=false.
    if app.config.get("EXPOSE_LEGACY_API", True):
        from app.members import members_bp
        from app.auth import auth_bp
        from app.rating import ratings_bp
        from app.clubs import clubs_bp
        from app.activities import activities_bp
        from app.invitations import invitation_bp
        from app.health.routes import health_bp

        app.register_blueprint(members_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(ratings_bp)
        app.register_blueprint(clubs_bp)
        app.register_blueprint(activities_bp)
        app.register_blueprint(invitation_bp)
        app.register_blueprint(health_bp)

    
    return app
