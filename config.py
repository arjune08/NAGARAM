import os
from datetime import timedelta
from urllib.parse import urlsplit, urlunsplit


class Config:
    # IMPORTANT: set SECRET_KEY in Vercel. The fallback is only for local use.
    SECRET_KEY = os.environ.get("SECRET_KEY", "urbanpulse-ai-local-development-key")

    # Keep the Flask-Login remember cookie long-lived. Authentication state is
    # restored from the database, never from client-side user data.
    PERSISTENT_LOGIN_DAYS = 3650
    PERSISTENT_LOGIN_LIFETIME = timedelta(days=PERSISTENT_LOGIN_DAYS)

    SESSION_COOKIE_NAME = "nagaram_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True if os.environ.get("VERCEL") else False
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_PATH = "/"
    SESSION_REFRESH_EACH_REQUEST = True
    PERMANENT_SESSION_LIFETIME = PERSISTENT_LOGIN_LIFETIME

    REMEMBER_COOKIE_NAME = "nagaram_remember"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True if os.environ.get("VERCEL") else False
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_PATH = "/"
    REMEMBER_COOKIE_DURATION = PERSISTENT_LOGIN_LIFETIME
    REMEMBER_COOKIE_REFRESH_EACH_REQUEST = True

    # Vercel/Neon integrations can expose different variable names. Prefer the
    # canonical DATABASE_URL, then the common Neon/Vercel aliases.
    DATABASE_URL = (
        os.environ.get("DATABASE_URL")
        or os.environ.get("POSTGRES_URL")
        or os.environ.get("POSTGRES_PRISMA_URL")
        or os.environ.get("NEON_DATABASE_URL")
    )

    if DATABASE_URL:
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        # psycopg 3 handles the SSL settings embedded in the Neon URL. Do not
        # add connect_timeout/pool arguments to the DBAPI connect call.
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True,
            "pool_recycle": 300,
        }
    elif os.environ.get("VERCEL"):
        # Never silently create/use SQLite on Vercel. A serverless filesystem is
        # not a database and would make login state/data disappear between
        # instances. The startup guard in app.py will fail clearly instead.
        SQLALCHEMY_DATABASE_URI = "postgresql+psycopg://invalid:invalid@localhost/invalid"
        SQLALCHEMY_ENGINE_OPTIONS = {}
        DATABASE_CONFIGURATION_ERROR = (
            "DATABASE_URL is missing. Configure the Neon PostgreSQL connection "
            "string as DATABASE_URL in Vercel Production."
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
