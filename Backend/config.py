import os


def env_bool(name: str, default: str = "false") -> bool:
    return os.environ.get(name, default).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Clerk configuration
    CLERK_SECRET_KEY = os.environ.get("CLERK_SECRET_KEY")
    CLERK_FRONTEND_API = os.environ.get("CLERK_FRONTEND_API")
    CLERK_AUDIENCE = os.environ.get("CLERK_AUDIENCE")  # fallback key some setups use
    CLERK_ISSUER = os.environ.get("CLERK_ISSUER")
    CLERK_JWKS_URL = os.environ.get("CLERK_JWKS_URL")

    # v1 single-club configuration
    SINGLE_CLUB_NAME = os.environ.get("SINGLE_CLUB_NAME")

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-hard-to-guess-string'

    # APScheduler configuration
    SCHEDULER_API_ENABLED = env_bool("SCHEDULER_API_ENABLED", "false")

    # Mail configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # Legacy API exposure
    # true  = expose old /api/... routes for dev/backward compatibility
    # false = expose only /api/v1/... routes for production
    EXPOSE_LEGACY_API = env_bool("EXPOSE_LEGACY_API", "true")


class TestingConfig(Config):
    Testing = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # in-memory SQLite for testing
    WTF_CSRF_ENABLED = False  # Disable CSRF for tests
    EXPOSE_LEGACY_API = True
    SCHEDULER_API_ENABLED = False

    
    
