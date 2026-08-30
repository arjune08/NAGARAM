from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from models import Complaint, InfrastructureAsset

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def landing():
    if current_user.is_authenticated:
        if current_user.role == 'admin': return redirect(url_for('admin.command_center'))
        if current_user.role == 'farmer': return redirect(url_for('farmer.dashboard'))
        if current_user.role == 'citizen': return redirect(url_for('citizen.dashboard'))
        if current_user.role == 'ngo': return redirect(url_for('ngo.dashboard'))
        if current_user.role == 'volunteer': return redirect(url_for('volunteer.dashboard'))
    total_complaints=Complaint.query.count(); resolved_complaints=Complaint.query.filter(Complaint.status.in_(['Resolved','Confirmed'])).count(); total_assets=InfrastructureAsset.query.count()
    return render_template('landing.html',total_complaints=total_complaints,resolved_complaints=resolved_complaints,total_assets=total_assets,sustainability_score=82.4)

@main_bp.route('/workspace')
@login_required
def workspace():
    if current_user.role=='farmer': return redirect(url_for('farmer.dashboard'))
    if current_user.role=='citizen': return redirect(url_for('citizen.dashboard'))
    if current_user.role=='admin': return redirect(url_for('admin.command_center'))
    if current_user.role=='ngo': return redirect(url_for('ngo.dashboard'))
    return redirect(url_for('volunteer.dashboard'))
