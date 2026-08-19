import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "urbanpulse-ai-super-secret-key-2026-sdg11")

    PERSISTENT_LOGIN_DAYS = 3650
    PERSISTENT_LOGIN_LIFETIME = timedelta(days=PERSISTENT_LOGIN_DAYS)

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = bool(os.environ.get("VERCEL"))
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_NAME = "nagaram_session"
    SESSION_REFRESH_EACH_REQUEST = True
    SESSION_COOKIE_PATH = "/"

    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = bool(os.environ.get("VERCEL"))
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_NAME = "nagaram_remember"
    REMEMBER_COOKIE_DURATION = PERSISTENT_LOGIN_LIFETIME
    REMEMBER_COOKIE_REFRESH_EACH_REQUEST = True
    REMEMBER_COOKIE_PATH = "/"
    PERMANENT_SESSION_LIFETIME = PERSISTENT_LOGIN_LIFETIME

    # Support both the explicit DATABASE_URL and the variable names commonly
    # created by Vercel/Neon integrations. Never hard-code a credential.
    DATABASE_URL = (
        os.environ.get("DATABASE_URL")
        or os.environ.get("POSTGRES_URL")
        or os.environ.get("POSTGRES_PRISMA_URL")
        or os.environ.get("NEON_DATABASE_URL")
    )

    if DATABASE_URL:
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True,
            "pool_recycle": 300,
        }
    elif os.environ.get("VERCEL"):
        # Never silently use SQLite in Vercel. A local SQLite database is not
        # persistent across serverless instances and would break user data.
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        SQLALCHEMY_ENGINE_OPTIONS = {}
        DATABASE_CONFIGURATION_ERROR = (
            "No PostgreSQL connection variable is configured. "
            "Set DATABASE_URL (or POSTGRES_URL) in Vercel Production."
        )
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///urbanpulse.db"
        SQLALCHEMY_ENGINE_OPTIONS = {}

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    if os.environ.get("VERCEL"):
        UPLOAD_FOLDER = "/tmp/urbanpulse_uploads"
    else:
        UPLOAD_FOLDER = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "static", "uploads"
        )

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    RATELIMIT_STORAGE_URL = "memory://"
