import os
from datetime import timedelta


class Config:
    # ---------------------------------------------------------
    # Security
    # ---------------------------------------------------------
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "urbanpulse-ai-development-secret-key"
    )

    # ---------------------------------------------------------
    # Database
    # ---------------------------------------------------------
    # Production:
    #   Set DATABASE_URL in Vercel Environment Variables.
    #
    # Local:
    #   Falls back to SQLite.
    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL:
        # Some providers still return postgres://
        # SQLAlchemy expects postgresql://
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace(
                "postgres://",
                "postgresql://",
                1
            )

        SQLALCHEMY_DATABASE_URI = DATABASE_URL

    else:
        # Local development only
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

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # ---------------------------------------------------------
    # Rate limiting
    # ---------------------------------------------------------
    RATELIMIT_STORAGE_URL = "memory://"
