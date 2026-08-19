import os
from datetime import timedelta


class Config:
    # ---------------------------------------------------------
    # Security
    # ---------------------------------------------------------
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "urbanpulse-ai-super-secret-key-2026-sdg11"
    )

    # ---------------------------------------------------------
    # Persistent login cookies
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # Database
    # ---------------------------------------------------------
    # Vercel production must provide DATABASE_URL pointing to the
    # persistent Neon PostgreSQL database. Never commit the real URL.
    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL:
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True,
            "pool_recycle": 300,
            "pool_timeout": 10,
            "connect_args": {"connect_timeout": 10},
        }
    else:
        # Local development fallback only. Production Vercel should not use this.
        SQLALCHEMY_DATABASE_URI = "sqlite:///urbanpulse.db"
        SQLALCHEMY_ENGINE_OPTIONS = {}

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---------------------------------------------------------
    # File uploads
    # ---------------------------------------------------------
    if os.environ.get("VERCEL"):
        UPLOAD_FOLDER = "/tmp/urbanpulse_uploads"
    else:
        UPLOAD_FOLDER = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "static",
            "uploads"
        )

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # ---------------------------------------------------------
    # Rate limiting
    # ---------------------------------------------------------
    RATELIMIT_STORAGE_URL = "memory://"
