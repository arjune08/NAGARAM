import os
from datetime import timedelta


class Config:
    # Production should provide a stable SECRET_KEY in Vercel. The fallback is
    # only for local development and is intentionally constant across restarts.
    SECRET_KEY = os.environ.get("SECRET_KEY", "urbanpulse-ai-local-development-key")

    PERSISTENT_LOGIN_DAYS = 3650
    PERSISTENT_LOGIN_LIFETIME = timedelta(days=PERSISTENT_LOGIN_DAYS)

    SESSION_COOKIE_NAME = "nagaram_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True if os.environ.get("VERCEL") else False
    SESSION_COOKIE_SAMESITE = "None" if os.environ.get("VERCEL") else "Lax"
    SESSION_COOKIE_DOMAIN = os.environ.get("SESSION_COOKIE_DOMAIN") or None
    SESSION_COOKIE_PATH = "/"
    SESSION_REFRESH_EACH_REQUEST = True
    PERMANENT_SESSION_LIFETIME = PERSISTENT_LOGIN_LIFETIME

    REMEMBER_COOKIE_NAME = "nagaram_remember"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True if os.environ.get("VERCEL") else False
    REMEMBER_COOKIE_SAMESITE = "None" if os.environ.get("VERCEL") else "Lax"
    REMEMBER_COOKIE_DOMAIN = os.environ.get("REMEMBER_COOKIE_DOMAIN") or None
    REMEMBER_COOKIE_PATH = "/"
    REMEMBER_COOKIE_DURATION = PERSISTENT_LOGIN_LIFETIME
    REMEMBER_COOKIE_REFRESH_EACH_REQUEST = True

    SESSION_PROTECTION = None

    # Supabase is PostgreSQL, so the existing SQLAlchemy models continue to
    # work without an ORM rewrite. Set SUPABASE_DB_URL (or DATABASE_URL) to the
    # Supabase Postgres connection string, including sslmode=require.
    DATABASE_URL = (
        os.environ.get("SUPABASE_DB_URL")
        or os.environ.get("DATABASE_URL")
        or os.environ.get("POSTGRES_URL")
        or os.environ.get("POSTGRES_PRISMA_URL")
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
        SQLALCHEMY_DATABASE_URI = "postgresql+psycopg://invalid:invalid@localhost/invalid"
        SQLALCHEMY_ENGINE_OPTIONS = {}
        DATABASE_CONFIGURATION_ERROR = (
            "SUPABASE_DB_URL/DATABASE_URL is missing. Configure the Supabase "
            "PostgreSQL connection string in Vercel Production."
        )
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///urbanpulse.db"
        SQLALCHEMY_ENGINE_OPTIONS = {}

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = (
        "/tmp/urbanpulse_uploads"
        if os.environ.get("VERCEL")
        else os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
    )

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    RATELIMIT_STORAGE_URL = "memory://"
