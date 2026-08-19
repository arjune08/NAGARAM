import os
from datetime import timedelta


class Config:
    # ---------------------------------------------------------
    # Security
    # ---------------------------------------------------------
    # IMPORTANT: set SECRET_KEY in Vercel Environment Variables to a
    # long random value. A stable key is required so signed Flask-Login
    # cookies remain valid across Vercel serverless instances/deployments.
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "urbanpulse-ai-super-secret-key-2026-sdg11"
    )

    # ---------------------------------------------------------
    # Persistent login cookies
    # ---------------------------------------------------------
    # Nagaram uses Flask-Login's remember cookie so a user stays signed in
    # after closing/reopening the browser. The long lifetime avoids forcing
    # users to log in repeatedly while still allowing explicit logout.
    # Passwords are NEVER stored in cookies.
    PERSISTENT_LOGIN_DAYS = 3650  # 10 years
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

    # Make the normal Flask session persistent for the same long period.
    # Flask-Login's remember cookie remains the recovery mechanism if the
    # browser clears the normal session cookie.
    PERMANENT_SESSION_LIFETIME = PERSISTENT_LOGIN_LIFETIME

    # ---------------------------------------------------------
    # Database
    # ---------------------------------------------------------
    # Production MUST provide DATABASE_URL (preferably managed PostgreSQL).
    # SQLite remains the local-development fallback only.
    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL:
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace(
                "postgres://",
                "postgresql://",
                1
            )
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///urbanpulse.db"

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
