from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError
from models import Complaint, InfrastructureAsset, db

main_bp = Blueprint('main', __name__)


def _landing_metrics():
    """Return live metrics when storage is available, otherwise safe defaults."""
    try:
        return {
            'total_complaints': Complaint.query.count(),
            'resolved_complaints': Complaint.query.filter(
                Complaint.status.in_(['Resolved', 'Confirmed'])
            ).count(),
            'total_assets': InfrastructureAsset.query.count(),
        }
    except SQLAlchemyError:
        db.session.rollback()
    except Exception:
        try:
            db.session.rollback()
        except Exception:
            pass
    return {'total_complaints': 0, 'resolved_complaints': 0, 'total_assets': 0}


@main_bp.route('/')
def landing():
    if current_user.is_authenticated:
        destinations = {
            'admin': 'admin.command_center',
            'farmer': 'farmer.dashboard',
            'citizen': 'citizen.dashboard',
            'ngo': 'ngo.dashboard',
            'volunteer': 'volunteer.dashboard',
        }
        endpoint = destinations.get(getattr(current_user, 'role', None))
        if endpoint:
            return redirect(url_for(endpoint))

    metrics = _landing_metrics()
    return render_template(
        'landing.html',
        **metrics,
        sustainability_score=82.4,
    )


@main_bp.route('/workspace')
@login_required
def workspace():
    destinations = {
        'farmer': 'farmer.dashboard',
        'citizen': 'citizen.dashboard',
        'admin': 'admin.command_center',
        'ngo': 'ngo.dashboard',
        'volunteer': 'volunteer.dashboard',
    }
    return redirect(url_for(destinations.get(current_user.role, 'main.landing')))
