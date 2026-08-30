import os
from datetime import timedelta
from urllib.parse import urlparse


def _database_url():
    """Return only a valid SQLAlchemy database URL.

    Vercel projects can contain unrelated DATABASE_URL variables. An invalid
    value must never be allowed to take the whole Flask function down.
    """
    candidates = (
        os.environ.get('NAGARAM_DATABASE_URL'),
        os.environ.get('SUPABASE_DB_URL'),
        os.environ.get('DATABASE_URL'),
        os.environ.get('POSTGRES_URL'),
        os.environ.get('NEON_DATABASE_URL'),
    )
    for value in candidates:
        if not value or not value.strip():
            continue
        value = value.strip()
        if value.startswith('postgres://'):
            value = value.replace('postgres://', 'postgresql+psycopg2://', 1)
        elif value.startswith('postgresql://'):
            value = value.replace('postgresql://', 'postgresql+psycopg2://', 1)
        # Accept only drivers available in requirements. Ignore malformed or
        # unrelated URLs instead of passing them to SQLAlchemy at runtime.
        if value.startswith('postgresql+psycopg2://'):
            return value
        if value.startswith('sqlite:///'):
            return value
    return None


def _is_postgres(url):
    return bool(url) and url.startswith('postgresql+psycopg2://')


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'nagaram-development-only-change-me'
    PERSISTENT_LOGIN_DAYS = int(os.environ.get('PERSISTENT_LOGIN_DAYS', '30'))
    PERSISTENT_LOGIN_LIFETIME = timedelta(days=PERSISTENT_LOGIN_DAYS)

    SESSION_COOKIE_NAME = 'nagaram_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = bool(os.environ.get('VERCEL'))
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_DOMAIN = os.environ.get('SESSION_COOKIE_DOMAIN') or None
    SESSION_COOKIE_PATH = '/'
    SESSION_REFRESH_EACH_REQUEST = True
    PERMANENT_SESSION_LIFETIME = PERSISTENT_LOGIN_LIFETIME

    REMEMBER_COOKIE_NAME = 'nagaram_remember'
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = bool(os.environ.get('VERCEL'))
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_DOMAIN = os.environ.get('REMEMBER_COOKIE_DOMAIN') or None
    REMEMBER_COOKIE_PATH = '/'
    REMEMBER_COOKIE_DURATION = PERSISTENT_LOGIN_LIFETIME
    REMEMBER_COOKIE_REFRESH_EACH_REQUEST = True
    SESSION_PROTECTION = None

    DATABASE_URL = _database_url()
    DATABASE_HOST = urlparse(DATABASE_URL).hostname if DATABASE_URL else None

    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_size': 2,
            'max_overflow': 0,
        }
        if _is_postgres(DATABASE_URL):
            SQLALCHEMY_ENGINE_OPTIONS['connect_args'] = {
                'connect_timeout': 10,
                'sslmode': 'require',
            }
    elif os.environ.get('VERCEL'):
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/nagaram_preview.db'
        SQLALCHEMY_ENGINE_OPTIONS = {'connect_args': {'check_same_thread': False}}
        DATABASE_CONFIGURATION_WARNING = (
            'No valid persistent PostgreSQL URL is configured. Supabase Auth '
            'persists accounts, while Vercel workspace data is temporary.'
        )
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///urbanpulse.db'
        SQLALCHEMY_ENGINE_OPTIONS = {}

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = '/tmp/nagaram_uploads' if os.environ.get('VERCEL') else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads'
    )
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    RATELIMIT_STORAGE_URL = 'memory://'
