from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from routes.auth import role_required
from models import db, VolunteerProfile, VolunteerApplication, InitiativeTask, Initiative

volunteer_bp = Blueprint('volunteer', __name__)

@volunteer_bp.route('/dashboard')
@login_required
@role_required('volunteer')
def dashboard():
    profile = VolunteerProfile.query.filter_by(user_id=current_user.id).first()
    applications = VolunteerApplication.query.filter_by(volunteer_id=profile.id).all() if profile else []
    completed_count = len([a for a in applications if a.status == 'Completed'])

    return render_template(
        'volunteer/dashboard.html',
        profile=profile,
        applications=applications,
        completed_count=completed_count
    )

@volunteer_bp.route('/opportunities')
@login_required
@role_required('volunteer')
def opportunities():
    profile = VolunteerProfile.query.filter_by(user_id=current_user.id).first()
    tasks = InitiativeTask.query.filter_by(status='Open').all()

    applied_task_ids = [a.task_id for a in profile.applications] if profile else []

    return render_template('volunteer/opportunities.html', tasks=tasks, profile=profile, applied_task_ids=applied_task_ids)

@volunteer_bp.route('/apply/<int:task_id>', methods=['POST'])
@login_required
@role_required('volunteer')
def apply_task(task_id):
    profile = VolunteerProfile.query.filter_by(user_id=current_user.id).first_or_404()
    task = InitiativeTask.query.get_or_404(task_id)

    existing = VolunteerApplication.query.filter_by(task_id=task.id, volunteer_id=profile.id).first()
    if existing:
        flash('You have already applied for this volunteer task.', 'warning')
        return redirect(url_for('volunteer.opportunities'))

    app = VolunteerApplication(task_id=task.id, volunteer_id=profile.id, status='Accepted')
    db.session.add(app)

    # Update counts
    task.initiative.current_volunteers += 1
    db.session.commit()

    flash(f'Application accepted for "{task.title}"! Thank you for volunteering.', 'success')
    return redirect(url_for('volunteer.activities'))

@volunteer_bp.route('/activities')
@login_required
@role_required('volunteer')
def activities():
    profile = VolunteerProfile.query.filter_by(user_id=current_user.id).first()
    applications = VolunteerApplication.query.filter_by(volunteer_id=profile.id).all() if profile else []
    return render_template('volunteer/activities.html', applications=applications, profile=profile)
