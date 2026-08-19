from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, NGOOrganization, VolunteerProfile


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
    """Only allow same-site relative redirects after authentication."""
    target = request.args.get('next', '')
    if target.startswith('/') and not target.startswith('//'):
        return target
    return None


def _login_and_redirect(user):
    # Flask-Login stores only the user id in the signed session/remember token;
    # the user record itself is always reloaded from persistent PostgreSQL.
    # remember=True is essential because Vercel functions are stateless.
    login_user(user, remember=True, fresh=True, duration=None)
    session.permanent = True
    session.modified = True

    next_url = _safe_next_url()
    if next_url:
        return redirect(next_url)

    if user.role == 'admin':
        return redirect(url_for('admin.command_center'))
    if user.role == 'ngo':
        return redirect(url_for('ngo.dashboard'))
    if user.role == 'volunteer':
        return redirect(url_for('volunteer.dashboard'))
    return redirect(url_for('citizen.dashboard'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return _login_and_redirect(current_user)

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid email address or password.', 'danger')
            return render_template('auth/login.html')

        response = _login_and_redirect(user)
        flash(f'Welcome back, {user.full_name}!', 'success')
        return response

    return render_template('auth/login.html')


@auth_bp.route('/register/citizen', methods=['GET', 'POST'])
def register_citizen():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        phone = request.form.get('phone', '').strip()

        if User.query.filter_by(email=email).first():
            flash('Email address is already registered.', 'warning')
            return render_template('auth/register_citizen.html')

        user = User(full_name=full_name, email=email, role='citizen', phone=phone)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        response = _login_and_redirect(user)
        flash('Registration successful! Welcome to Nagaram.', 'success')
        return response

    return render_template('auth/register_citizen.html')


@auth_bp.route('/register/ngo', methods=['GET', 'POST'])
def register_ngo():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        org_name = request.form.get('org_name', '').strip()
        reg_num = request.form.get('reg_number', '').strip()
        category = request.form.get('category', 'Environment')

        if User.query.filter_by(email=email).first():
            flash('Email address is already registered.', 'warning')
            return render_template('auth/register_ngo.html')

        user = User(full_name=full_name, email=email, role='ngo')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        ngo = NGOOrganization(
            user_id=user.id,
            name=org_name,
            registration_number=reg_num,
            category=category,
            verification_status='Pending'
        )
        db.session.add(ngo)
        db.session.commit()

        response = _login_and_redirect(user)
        flash('NGO Registration submitted for verification!', 'success')
        return response

    return render_template('auth/register_ngo.html')


@auth_bp.route('/register/volunteer', methods=['GET', 'POST'])
def register_volunteer():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        skills = request.form.get('skills', '')
        availability = request.form.get('availability', 'Weekends')

        if User.query.filter_by(email=email).first():
            flash('Email address is already registered.', 'warning')
            return render_template('auth/register_volunteer.html')

        user = User(full_name=full_name, email=email, role='volunteer')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        vol = VolunteerProfile(
            user_id=user.id,
            skills=skills,
            availability=availability
        )
        db.session.add(vol)
        db.session.commit()

        response = _login_and_redirect(user)
        flash('Volunteer Registration completed!', 'success')
        return response

    return render_template('auth/register_volunteer.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have logged out successfully.', 'info')
    return redirect(url_for('main.landing'))
