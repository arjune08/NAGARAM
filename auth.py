from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from models import db, User, NGOOrganization, VolunteerProfile
from login_models import UserLoginEvent
from farmer_models import FarmerProfile
from supabase_auth import sign_up as supabase_sign_up, sign_in as supabase_sign_in, SupabaseAuthError

auth_bp = Blueprint('auth', __name__)


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.path))
            if current_user.role not in roles:
                flash('This workspace is not available for your account role.', 'danger')
                return render_template('403.html'), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def _safe_next_url():
    target = request.args.get('next') or request.form.get('next') or ''
    return target if target.startswith('/') and not target.startswith('//') else None


def _record_login_event(user, email, event_type):
    db.session.add(UserLoginEvent(
        user_id=user.id if user else None,
        email=(email or '').strip().lower(),
        event_type=event_type,
    ))


def _workspace_redirect(user):
    next_url = _safe_next_url()
    if next_url:
        return redirect(next_url)
    routes = {
        'admin': 'admin.command_center',
        'ngo': 'ngo.dashboard',
        'volunteer': 'volunteer.dashboard',
        'farmer': 'farmer.dashboard',
    }
    return redirect(url_for(routes.get(user.role, 'citizen.dashboard')))


def _store_supabase_session(remote):
    remote_user = remote.get('user') or {}
    access_token = remote.get('access_token') or ''
    refresh_token = remote.get('refresh_token') or ''
    if not remote_user or not access_token:
        raise SupabaseAuthError('Account created, but email confirmation is required before signing in.')
    session['supabase_access_token'] = access_token
    session['supabase_refresh_token'] = refresh_token
    session['supabase_user_id'] = remote_user.get('id', '')
    session['supabase_email'] = remote_user.get('email', '')
    session['supabase_metadata'] = remote_user.get('user_metadata') or {}
    session.permanent = True
    session.modified = True


def _login_and_redirect(user, event_type='login', remember=False):
    login_user(user, remember=remember, fresh=True)
    session.permanent = True
    session.modified = True
    try:
        _record_login_event(user, user.email, event_type)
        db.session.commit()
    except Exception:
        try:
            db.session.rollback()
        except Exception:
            pass
    return _workspace_redirect(user)


def _ensure_local_user(email, password, metadata):
    user = User.query.filter_by(email=email).first()
    role = metadata.get('role') or 'citizen'
    full_name = metadata.get('full_name') or email.split('@')[0]
    phone = metadata.get('phone') or ''
    if user is None:
        user = User(full_name=full_name, email=email, role=role, phone=phone)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
    else:
        user.full_name = full_name or user.full_name
        user.role = role or user.role
        user.phone = phone or user.phone
        db.session.flush()
    if user.role == 'farmer' and not FarmerProfile.query.filter_by(user_id=user.id).first():
        db.session.add(FarmerProfile(
            user_id=user.id,
            village=metadata.get('village') or 'Demo Gram',
            district=metadata.get('district') or '',
            preferred_language=metadata.get('preferred_language') or 'en',
        ))
    return user


def _supabase_metadata(form, role):
    return {
        'full_name': form.get('full_name', '').strip(),
        'role': role,
        'phone': form.get('phone', '').strip(),
        'village': form.get('village', '').strip(),
        'district': form.get('district', '').strip(),
        'preferred_language': form.get('language', 'en'),
    }


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Deliberately do not touch current_user on GET. This endpoint must stay
    # safe even when a stale Flask-Login session is present.
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    remember = request.form.get('remember') == 'on'
    if not email or not password:
        flash('Enter your email and password.', 'warning')
        return render_template('login.html')

    try:
        remote = supabase_sign_in(email, password)
        remote_user = remote.get('user') or {}
        metadata = remote_user.get('user_metadata') or {}
        _store_supabase_session(remote)
    except SupabaseAuthError as exc:
        message = str(exc)
        if 'Invalid login credentials' in message:
            message = 'Invalid email address or password.'
        flash(message, 'danger')
        return render_template('login.html')

    try:
        user = _ensure_local_user(email, password, metadata)
        response = _login_and_redirect(user, 'supabase_login_success', remember=remember)
    except (SQLAlchemyError, Exception) as exc:
        try:
            db.session.rollback()
        except Exception:
            pass
        # Keep the verified Supabase session in the signed cookie. The next
        # request can restore the local user once the serverless DB is ready.
        flash('Your identity was verified, but the workspace is temporarily unavailable. Please try again in a moment.', 'warning')
        return redirect(url_for('auth.login'))

    flash(f'Welcome back, {user.full_name}!', 'success')
    return response


def _create_basic_user(full_name, email, password, phone, role):
    if not full_name or not email or len(password) < 6:
        raise ValueError('Enter a name, valid email and a password of at least 6 characters.')
    if User.query.filter_by(email=email).first():
        raise ValueError('Email address is already registered. Please sign in instead.')
    user = User(full_name=full_name, email=email, role=role, phone=phone)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    return user


def _registration_failed(template_name, message):
    try:
        db.session.rollback()
    except Exception:
        pass
    flash(message, 'danger')
    return render_template(template_name)


def _register(template, role, profile_factory, success):
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    metadata = _supabase_metadata(request.form, role)
    if not metadata['full_name'] or not email or len(password) < 6:
        flash('Enter a name, valid email and a password of at least 6 characters.', 'warning')
        return render_template(template)

    try:
        remote = supabase_sign_up(email, password, metadata)
    except SupabaseAuthError as exc:
        message = str(exc)
        if 'already registered' in message.lower():
            message = 'This email is already registered. Please sign in instead.'
        flash(f'Account could not be created: {message}', 'danger')
        return render_template(template)

    try:
        user = _create_basic_user(metadata['full_name'], email, password, metadata['phone'], role)
        profile_factory(user)
        db.session.commit()
    except ValueError as exc:
        return _registration_failed(template, str(exc))
    except Exception:
        return _registration_failed(template, 'Your account was created, but the workspace profile could not be prepared. Please sign in again.')

    try:
        _store_supabase_session(remote)
        response = _login_and_redirect(user, 'supabase_registration', remember=True)
    except SupabaseAuthError as exc:
        flash(str(exc), 'info')
        return redirect(url_for('auth.login'))
    except Exception:
        return _registration_failed(template, 'Your account was created, but automatic sign-in failed. Please sign in manually.')

    flash(success, 'success')
    return response


@auth_bp.route('/register/citizen', methods=['GET', 'POST'])
def register_citizen():
    if request.method == 'POST':
        return _register('auth/register_citizen.html', 'citizen', lambda user: None, 'Registration successful! Welcome to NAGARAM.')
    return render_template('auth/register_citizen.html')


@auth_bp.route('/register/farmer', methods=['GET', 'POST'])
def register_farmer():
    if request.method == 'POST':
        return _register(
            'auth/register_farmer.html', 'farmer',
            lambda user: db.session.add(FarmerProfile(
                user_id=user.id,
                village=request.form.get('village', 'Demo Gram').strip() or 'Demo Gram',
                district=request.form.get('district', '').strip(),
                preferred_language=request.form.get('language', 'en'),
            )),
            'Farmer account created. Your Farm Workspace is ready.'
        )
    return render_template('auth/register_farmer.html')


@auth_bp.route('/register/ngo', methods=['GET', 'POST'])
def register_ngo():
    if request.method == 'POST':
        return _register(
            'auth/register_ngo.html', 'ngo',
            lambda user: db.session.add(NGOOrganization(
                user_id=user.id,
                name=request.form.get('org_name', '').strip(),
                registration_number=request.form.get('reg_number', '').strip(),
                category=request.form.get('category', 'Environment'),
                verification_status='Pending',
            )),
            'Organization registration submitted successfully!'
        )
    return render_template('auth/register_ngo.html')


@auth_bp.route('/register/volunteer', methods=['GET', 'POST'])
def register_volunteer():
    if request.method == 'POST':
        return _register(
            'auth/register_volunteer.html', 'volunteer',
            lambda user: db.session.add(VolunteerProfile(
                user_id=user.id,
                skills=request.form.get('skills', ''),
                availability=request.form.get('availability', 'Weekends'),
            )),
            'Field worker registration completed!'
        )
    return render_template('auth/register_volunteer.html')


@auth_bp.route('/logout')
@login_required
def logout():
    try:
        user = current_user._get_current_object()
        _record_login_event(user, user.email, 'logout')
        db.session.commit()
    except Exception:
        try:
            db.session.rollback()
        except Exception:
            pass
    logout_user()
    session.clear()
    flash('You have logged out successfully.', 'info')
    return redirect(url_for('main.landing'))
