from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
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
    target = request.args.get('next') or request.form.get('next') or ''
    if target.startswith('/') and not target.startswith('//'):
        return target
    return None


def _login_and_redirect(user):
    login_user(user, remember=True, fresh=True)
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


def _create_user(full_name, email, password, role, phone=None):
    user = User(
        full_name=full_name,
        email=email,
        role=role,
        phone=phone or None,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()  # assigns the database ID before related rows are made
    return user


def _registration_error(template, message):
    db.session.rollback()
    flash(message, 'danger')
    return render_template(template)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return _login_and_redirect(current_user)

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        try:
            user = User.query.filter_by(email=email).first()
        except SQLAlchemyError:
            db.session.rollback()
            flash('Login service is temporarily unavailable. Please try again.', 'danger')
            return render_template('login.html')

        if not user or not user.check_password(password):
            flash('Invalid email address or password.', 'danger')
            return render_template('login.html')

        response = _login_and_redirect(user)
        flash(f'Welcome back, {user.full_name}!', 'success')
        return response

    return render_template('login.html')


@auth_bp.route('/register/citizen', methods=['GET', 'POST'])
def register_citizen():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        phone = request.form.get('phone', '').strip()

        if not full_name or not email or not password:
            flash('Name, email, and password are required.', 'warning')
            return render_template('auth/register_citizen.html')

        try:
            user = _create_user(full_name, email, password, 'citizen', phone)
            db.session.commit()
        except IntegrityError:
            return _registration_error(
                'auth/register_citizen.html', 'Email address is already registered.'
            )
        except SQLAlchemyError:
            return _registration_error(
                'auth/register_citizen.html',
                'We could not save your account. Please try again.',
            )

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

        if not full_name or not email or not password or not org_name:
            flash('Please complete all required registration fields.', 'warning')
            return render_template('auth/register_ngo.html')

        try:
            user = _create_user(full_name, email, password, 'ngo')
            db.session.add(NGOOrganization(
                user_id=user.id,
                name=org_name,
                registration_number=reg_num,
                category=category,
                verification_status='Pending',
            ))
            db.session.commit()
        except IntegrityError:
            return _registration_error(
                'auth/register_ngo.html', 'Email address is already registered.'
            )
        except SQLAlchemyError:
            return _registration_error(
                'auth/register_ngo.html',
                'We could not save your registration. Please try again.',
            )

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

        if not full_name or not email or not password:
            flash('Name, email, and password are required.', 'warning')
            return render_template('auth/register_volunteer.html')

        try:
            user = _create_user(full_name, email, password, 'volunteer')
            db.session.add(VolunteerProfile(
                user_id=user.id,
                skills=skills,
                availability=availability,
            ))
            db.session.commit()
        except IntegrityError:
            return _registration_error(
                'auth/register_volunteer.html', 'Email address is already registered.'
            )
        except SQLAlchemyError:
            return _registration_error(
                'auth/register_volunteer.html',
                'We could not save your registration. Please try again.',
            )

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
