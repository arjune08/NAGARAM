from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, NGOOrganization, VolunteerProfile
from login_models import UserLoginEvent
from farmer_models import FarmerProfile

auth_bp = Blueprint('auth', __name__)


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for('auth.login', next=request.path))
            if current_user.role not in roles:
                flash("Unauthorized access for your account role.", "danger")
                return render_template('errors/403.html'), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def _safe_next_url():
    target = request.args.get('next') or request.form.get('next') or ''
    return target if target.startswith('/') and not target.startswith('//') else None


def _record_login_event(user, email, event_type):
    db.session.add(UserLoginEvent(user_id=user.id if user else None, email=(email or '').strip().lower(), event_type=event_type))


def _login_and_redirect(user, event_type='login', remember=False):
    login_user(user, remember=remember, fresh=True)
    session.permanent = True
    session.modified = True
    _record_login_event(user, user.email, event_type)
    db.session.commit()
    next_url = _safe_next_url()
    if next_url:
        return redirect(next_url)
    if user.role == 'admin':
        return redirect(url_for('admin.command_center'))
    if user.role == 'ngo':
        return redirect(url_for('ngo.dashboard'))
    if user.role == 'volunteer':
        return redirect(url_for('volunteer.dashboard'))
    if user.role == 'farmer':
        return redirect(url_for('farmer.dashboard'))
    return redirect(url_for('citizen.dashboard'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return _login_and_redirect(current_user, 'session_refresh', remember=True)
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            _record_login_event(user, email, 'login_failed')
            db.session.commit()
            flash('Invalid email address or password.', 'danger')
            return render_template('login.html')
        response = _login_and_redirect(user, 'login_success', remember=remember)
        flash(f'Welcome back, {user.full_name}!', 'success')
        return response
    return render_template('login.html')


def _create_basic_user(full_name, email, password, phone, role):
    if not full_name or not email or len(password) < 6:
        raise ValueError('Enter a name, valid email and a password of at least 6 characters.')
    if User.query.filter_by(email=email).first():
        raise ValueError('Email address is already registered.')
    user = User(full_name=full_name, email=email, role=role, phone=phone)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


@auth_bp.route('/register/citizen', methods=['GET', 'POST'])
def register_citizen():
    if request.method == 'POST':
        try:
            user = _create_basic_user(request.form.get('full_name', '').strip(), request.form.get('email', '').strip().lower(), request.form.get('password', ''), request.form.get('phone', '').strip(), 'citizen')
        except ValueError as e:
            flash(str(e), 'warning')
            return render_template('auth/register_citizen.html')
        response = _login_and_redirect(user, 'registration_login', remember=True)
        flash('Registration successful! Welcome to Nagaram.', 'success')
        return response
    return render_template('auth/register_citizen.html')


@auth_bp.route('/register/farmer', methods=['GET', 'POST'])
def register_farmer():
    if request.method == 'POST':
        try:
            user = _create_basic_user(request.form.get('full_name', '').strip(), request.form.get('email', '').strip().lower(), request.form.get('password', ''), request.form.get('phone', '').strip(), 'farmer')
            db.session.add(FarmerProfile(user_id=user.id, village=request.form.get('village', 'Demo Gram').strip() or 'Demo Gram', district=request.form.get('district', '').strip(), preferred_language=request.form.get('language', 'en')))
            db.session.commit()
        except ValueError as e:
            flash(str(e), 'warning')
            return render_template('auth/register_farmer.html')
        except Exception:
            db.session.rollback()
            flash('We could not create the farmer profile. Please try again.', 'danger')
            return render_template('auth/register_farmer.html')
        response = _login_and_redirect(user, 'registration_login', remember=True)
        flash('Farmer account created. Your Farm Workspace is ready.', 'success')
        return response
    return render_template('auth/register_farmer.html')


@auth_bp.route('/register/ngo', methods=['GET', 'POST'])
def register_ngo():
    if request.method == 'POST':
        try:
            user = _create_basic_user(request.form.get('full_name', '').strip(), request.form.get('email', '').strip().lower(), request.form.get('password', ''), '', 'ngo')
            db.session.add(NGOOrganization(user_id=user.id, name=request.form.get('org_name', '').strip(), registration_number=request.form.get('reg_number', '').strip(), category=request.form.get('category', 'Environment'), verification_status='Pending'))
            db.session.commit()
        except ValueError as e:
            flash(str(e), 'warning')
            return render_template('auth/register_ngo.html')
        except Exception:
            db.session.rollback()
            flash('We could not complete NGO registration. Please try again.', 'danger')
            return render_template('auth/register_ngo.html')
        response = _login_and_redirect(user, 'registration_login', remember=True)
        flash('NGO Registration submitted for verification!', 'success')
        return response
    return render_template('auth/register_ngo.html')


@auth_bp.route('/register/volunteer', methods=['GET', 'POST'])
def register_volunteer():
    if request.method == 'POST':
        try:
            user = _create_basic_user(request.form.get('full_name', '').strip(), request.form.get('email', '').strip().lower(), request.form.get('password', ''), '', 'volunteer')
            db.session.add(VolunteerProfile(user_id=user.id, skills=request.form.get('skills', ''), availability=request.form.get('availability', 'Weekends')))
            db.session.commit()
        except ValueError as e:
            flash(str(e), 'warning')
            return render_template('auth/register_volunteer.html')
        except Exception:
            db.session.rollback()
            flash('We could not complete volunteer registration. Please try again.', 'danger')
            return render_template('auth/register_volunteer.html')
        response = _login_and_redirect(user, 'registration_login', remember=True)
        flash('Volunteer Registration completed!', 'success')
        return response
    return render_template('auth/register_volunteer.html')


@auth_bp.route('/logout')
@login_required
def logout():
    _record_login_event(current_user, current_user.email, 'logout')
    db.session.commit()
    logout_user()
    session.clear()
    flash('You have logged out successfully.', 'info')
    return redirect(url_for('main.landing'))