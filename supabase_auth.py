import json
import os
from urllib import request, error

DEFAULT_SUPABASE_URL = 'https://kawujopsewnjbwinkccq.supabase.co'
DEFAULT_SUPABASE_PUBLISHABLE_KEY = 'sb_publishable_RFirtyvffOdVUepmmUMJTg_lnYis8YY'

class SupabaseAuthError(Exception):
    pass

def _settings():
    return (
        os.environ.get('SUPABASE_URL', DEFAULT_SUPABASE_URL).rstrip('/'),
        os.environ.get('SUPABASE_PUBLISHABLE_KEY', DEFAULT_SUPABASE_PUBLISHABLE_KEY),
    )

def is_enabled():
    url, key = _settings()
    return bool(url and key)

def _call(path, payload):
    base, key = _settings()
    if not base or not key:
        raise SupabaseAuthError('Supabase authentication is not configured.')
    body = json.dumps(payload).encode('utf-8')
    req = request.Request(
        f'{base}{path}', data=body, method='POST',
        headers={'apikey': key, 'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
    )
    try:
        with request.urlopen(req, timeout=12) as response:
            return json.loads(response.read().decode('utf-8'))
    except error.HTTPError as exc:
        try:
            detail = json.loads(exc.read().decode('utf-8'))
            message = detail.get('msg') or detail.get('message') or detail.get('error_description')
        except Exception:
            message = None
        raise SupabaseAuthError(message or 'Supabase authentication request failed.') from exc
    except Exception as exc:
        raise SupabaseAuthError('Unable to reach the authentication service. Please try again.') from exc

def sign_up(email, password, metadata):
    return _call('/auth/v1/signup', {'email': email, 'password': password, 'data': metadata})

def sign_in(email, password):
    return _call('/auth/v1/token?grant_type=password', {'email': email, 'password': password})

def refresh_session(refresh_token):
    if not refresh_token:
        raise SupabaseAuthError('No refresh token is available.')
    return _call('/auth/v1/token?grant_type=refresh_token', {'refresh_token': refresh_token})

def get_user(access_token):
    """Resolve a persisted Supabase session without relying on local database state."""
    base, key = _settings()
    if not access_token:
        raise SupabaseAuthError('No access token is available.')
    req = request.Request(
        f'{base}/auth/v1/user', method='GET',
        headers={'apikey': key, 'Authorization': f'Bearer {access_token}'}
    )
    try:
        with request.urlopen(req, timeout=8) as response:
            return json.loads(response.read().decode('utf-8'))
    except error.HTTPError as exc:
        try:
            detail = json.loads(exc.read().decode('utf-8'))
            message = detail.get('msg') or detail.get('message') or detail.get('error_description')
        except Exception:
            message = None
        raise SupabaseAuthError(message or 'Supabase session is no longer valid.') from exc
    except Exception as exc:
        raise SupabaseAuthError('Unable to verify the saved sign-in session.') from exc
