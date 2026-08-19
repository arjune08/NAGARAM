import os
from datetime import timedelta


class Config:
    # ---------------------------------------------------------
    # Security
    # ---------------------------------------------------------
    # Keep one stable secret in production so Flask-Login session
    # cookies remain valid across Vercel serverless instances.
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "urbanpulse-ai-super-secret-key-2026-sdg11"
    )

    # Session cookies must survive requests routed to different Vercel
    # serverless instances. They are HTTP-only and secure in production.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = bool(os.environ.get("VERCEL"))
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_NAME = "nagaram_session"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = bool(os.environ.get("VERCEL"))
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_NAME = "nagaram_remember"
    REMEMBER_COOKIE_DURATION = timedelta(days=30)

    # ---------------------------------------------------------
    # Database
    # ---------------------------------------------------------
    # Production should provide DATABASE_URL (preferably managed PostgreSQL).
    # SQLite remains the local-development fallback.
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
    # Session
    # ---------------------------------------------------------
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

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
