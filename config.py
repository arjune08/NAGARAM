import os
from datetime import timedelta

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
    SESSION_PROTECTION = 'basic'
    DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL') or os.environ.get('POSTGRES_PRISMA_URL') or os.environ.get('NEON_DATABASE_URL')
    if DATABASE_URL:
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+psycopg2://', 1)
        elif DATABASE_URL.startswith('postgresql://'):
            DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg2://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
        SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True, 'pool_recycle': 300, 'connect_args': {'connect_timeout': 10}}
    elif os.environ.get('VERCEL'):
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/nagaram_preview.db'
        SQLALCHEMY_ENGINE_OPTIONS = {}
        DATABASE_CONFIGURATION_WARNING = 'DATABASE_URL is not configured; Supabase Auth is persistent but workspace data is using temporary preview storage.'
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///urbanpulse.db'
        SQLALCHEMY_ENGINE_OPTIONS = {}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = '/tmp/nagaram_uploads' if os.environ.get('VERCEL') else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    RATELIMIT_STORAGE_URL = 'memory://'
