from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from models import Complaint, InfrastructureAsset, Zone, SustainabilityIndicator

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def landing():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.command_center'))
        elif current_user.role == 'citizen':
            return redirect(url_for('citizen.dashboard'))
        elif current_user.role == 'ngo':
            return redirect(url_for('ngo.dashboard'))
        elif current_user.role == 'volunteer':
            return redirect(url_for('volunteer.dashboard'))

    # Public landing page metrics
    total_complaints = Complaint.query.count()
    resolved_complaints = Complaint.query.filter(Complaint.status.in_(['Resolved', 'Confirmed'])).count()
    total_assets = InfrastructureAsset.query.count()
    sustainability_score = 82.4

    return render_template(
        'landing.html',
        total_complaints=total_complaints,
        resolved_complaints=resolved_complaints,
        total_assets=total_assets,
        sustainability_score=sustainability_score
    )
