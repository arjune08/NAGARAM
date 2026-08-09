from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from auth import role_required
from models import db, NGOOrganization, Initiative, InitiativeTask, VolunteerApplication, VolunteerProfile
from datetime import datetime

ngo_bp = Blueprint('ngo', __name__)

@ngo_bp.route('/dashboard')
@login_required
@role_required('ngo')
def dashboard():
    ngo = NGOOrganization.query.filter_by(user_id=current_user.id).first()
    initiatives = Initiative.query.filter_by(ngo_id=ngo.id).all() if ngo else []
    total_volunteers = sum([i.current_volunteers for i in initiatives])
    active_initiatives = len([i for i in initiatives if i.status == 'Active'])
    return render_template('ngo/dashboard.html', ngo=ngo, initiatives=initiatives, total_volunteers=total_volunteers, active_initiatives=active_initiatives)

@ngo_bp.route('/initiatives', methods=['GET', 'POST'])
@login_required
@role_required('ngo')
def initiatives():
    ngo = NGOOrganization.query.filter_by(user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        target = request.form.get('target_volunteers', 10)
        location = request.form.get('location', '').strip()
        init = Initiative(ngo_id=ngo.id, title=title, description=description, target_volunteers=int(target), location=location, start_date=datetime.utcnow())
        db.session.add(init)
        db.session.commit()
        flash(f'Initiative "{title}" created successfully!', 'success')
        return redirect(url_for('ngo.initiatives'))
    all_initiatives = Initiative.query.filter_by(ngo_id=ngo.id).all()
    return render_template('ngo/initiatives.html', initiatives=all_initiatives, ngo=ngo)

@ngo_bp.route('/volunteers')
@login_required
@role_required('ngo')
def volunteers():
    ngo = NGOOrganization.query.filter_by(user_id=current_user.id).first_or_404()
    initiative_ids = [i.id for i in ngo.initiatives]
    tasks = InitiativeTask.query.filter(InitiativeTask.initiative_id.in_(initiative_ids)).all() if initiative_ids else []
    task_ids = [t.id for t in tasks]
    applications = VolunteerApplication.query.filter(VolunteerApplication.task_id.in_(task_ids)).all() if task_ids else []
    return render_template('ngo/volunteers.html', applications=applications, tasks=tasks)
