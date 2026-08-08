from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, NGOOrganization, VolunteerProfile
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for('auth.login'))
            if current_user.role not in roles:
                flash("Unauthorized access for your account role.", "danger")
                return render_template('errors/403.html'), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.landing'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid email address or password.', 'danger')
            return render_template('auth/login.html')

        login_user(user, remember=remember)
        flash(f'Welcome back, {user.full_name}!', 'success')

        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)

        if user.role == 'admin':
            return redirect(url_for('admin.command_center'))
        elif user.role == 'ngo':
            return redirect(url_for('ngo.dashboard'))
        elif user.role == 'volunteer':
            return redirect(url_for('volunteer.dashboard'))
        else:
            return redirect(url_for('citizen.dashboard'))

    return render_template('auth/login.html')

@auth_bp.route('/register/citizen', methods=['GET', 'POST'])
def register_citizen():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        phone = request.form.get('phone', '').strip()

        if User.query.filter_by(email=email).first():
            flash('Email address is already registered.', 'warning')
            return render_template('auth/register_citizen.html')

        user = User(full_name=full_name, email=email, role='citizen', phone=phone)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('Registration successful! Welcome to UrbanPulse AI.', 'success')
        return redirect(url_for('citizen.dashboard'))

    return render_template('auth/register_citizen.html')

@auth_bp.route('/register/ngo', methods=['GET', 'POST'])
def register_ngo():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
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

        login_user(user)
        flash('NGO Registration submitted for verification!', 'success')
        return redirect(url_for('ngo.dashboard'))

    return render_template('auth/register_ngo.html')

@auth_bp.route('/register/volunteer', methods=['GET', 'POST'])
def register_volunteer():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
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

        login_user(user)
        flash('Volunteer Registration completed!', 'success')
        return redirect(url_for('volunteer.dashboard'))

    return render_template('auth/register_volunteer.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out successfully.', 'info')
    return redirect(url_for('main.landing'))
